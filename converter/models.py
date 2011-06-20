#!/usr/bin/env python
# encoding: utf-8
import os.path
import re
import sys
from datetime import datetime
from htmlentitydefs import name2codepoint
from struct import pack, unpack
from django.conf import settings
from django.core.files import File as DjangoFile
from django.db import models, connections, transaction
from django.utils.html import strip_tags as strip_html_tags
from board.models import Thread, Post, File, FileType, Section, DeniedIP
from board.tools import get_key, print_flush


SUBSTITUTIONS = [(re.compile(r), s) for r, s in (
    (r'<strong>(.*)</strong>', r'**\1**'),
    (r'<em>(.*)</em>', r'*\1*'),
    (r'&gt;', '>'),
    (r'>>(\d{1,10})</a>', r'>>\1</a>'),
    (r'<br />', '\n'),
    (r'<span class="unkfunc">>(.*)</span>', r'>\1'),
    (r'<span class="spoiler">(.*)</span>', r'%%\1%%'),
)]


def convert_ip(ip):
    """Converts IP from wakaba format to its normal string representation.
    Wakaba packs ip to the long integer with perl's pack() function.
    """
    try:
        adr = unpack('4B', pack('>L', int(ip)))  # 4-tuple
    except Exception as e:
        raise ValueError(e)
    return '.'.join(str(i) for i in adr)


def unescape(text):
    """Unescapes HTML entitles to unicode chars.

    Example: &amp; -> &.
    """
    def fixup(m):
        text = m.group(0)
        if text[:2] == '&#':  # character reference
            try:
                if text[:3] == '&#x':
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:  # named entity
            try:
                text = unichr(name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text  # leave as is
    return re.sub('&#?\w+;', fixup, text)


def parse_video(text):
    """Extracts video URL from wakaba's HTML."""
    if not text:
        return text
    v = (r'<object width="320" height="262"><param name="movie" value="'
        r'(?P<url>http://www\.youtube\.com/v/(?P<id>[A-Za-z0-9=_-]{11}))">'
        r'</param><param name="wmode" value="transparent"></param><embed'
        r' src="\1" type="application/x-shockwave-flash"'
        r' wmode="transparent" width="320" height="262"></embed></object>')
    return re.sub(v, r'http://www.youtube.com/watch?v=\g<id>', text)


def strip_tags(text):
    """Converts some HTML tags to Markdown and strips other ones."""
    for r, s in SUBSTITUTIONS:
        text = re.sub(r, s, text)
    return unescape(strip_html_tags(text))


class ConvertError(Exception):
    pass


class WakabaPost(models.Model):
    """Used as temporary storage of wakaba posts on database convertation.
    This model represents wakaba post with some additions, like:
    - section slug (wakaba doesn't have sections)
    - some fields renamed (num -> pid, trip -> tripcode) to match chieftain
    style
    - some fields removed (last_visit, thumb_size etc.)
    """
    pid = models.IntegerField()
    section_slug = models.CharField(max_length=10)
    parent = models.IntegerField(null=True)
    date = models.DateTimeField(null=True)
    ip = models.CharField(null=True, max_length=50)
    poster = models.TextField(null=True)
    tripcode = models.TextField(null=True)
    email = models.TextField(null=True)
    topic = models.TextField(null=True)
    password = models.TextField(null=True)
    message = models.TextField(null=True)
    image = models.TextField(null=True)
    image_md5 = models.TextField(null=True)
    image_width = models.IntegerField(null=True)
    image_height = models.IntegerField(null=True)
    thumb = models.TextField(null=True)
    video = models.TextField(null=True)
    is_pinned = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)

    def __unicode__(self):
        return u'{}/{}'.format(self.section_slug, self.pid)


class WakabaBan(models.Model):
    ip = models.IPAddressField()
    reason = models.CharField(max_length=128)


class WakabaInitializer(object):
    """Copies posts from all wakaba databases to one big temporary db.

    Initializer contains 'fields' field (2 or 3-tuple), that determines
    convertable fields in format:
    * wakaba field name
    * chieftain field name in the temporary model
    * convert function (optional)
    Also if chieftain field name is None, it won't be converted.
    """
    fields = (
        ('num', 'pid'),
        ('parent', 'parent'),
        ('timestamp', 'date', lambda f: datetime.fromtimestamp(float(f))),
        ('lasthit', None),
        ('ip', 'ip', convert_ip),
        ('date', None),
        ('name', 'poster'),
        ('trip', 'tripcode', lambda f: f.strip('!')),
        ('email', 'email'),
        ('subject', 'topic'),
        ('password', 'password', get_key),
        ('comment', 'message', strip_tags),
        ('image', 'image'),
        ('size', None),
        ('md5', 'image_md5'),
        ('width', 'image_width'),
        ('height', 'image_height'),
        ('thumbnail', 'thumb'),
        ('tn_width', None),
        ('tn_height', None),
        ('video', 'video', parse_video),
        ('sticky', 'is_pinned', bool),
        ('closed', 'is_closed', bool),
    )

    def __init__(self, prefix='comments_'):
        super(WakabaInitializer, self).__init__()
        self.prefix = prefix
        self.cursor = connections['wakaba'].cursor()
        self.tables = self.get_tables_list()

    def get_tables_list(self):
        """Returns list of wakaba section slugs without table prefix.
        For example, if tables are: ['comments_b', 'comments_c'],
        it would return ['b', 'c'].
        """
        self.cursor.execute('SHOW tables')
        return [
            i[0].replace(self.prefix, '')
            for i in self.cursor.fetchall()
            if i[0].startswith(self.prefix)
        ]

    def get_bans(self):
        fields = ['ip', 'reason']
        sql = 'SELECT ival1, comment FROM admin WHERE type = "ipban"'
        self.cursor.execute(sql)
        for i in self.cursor.fetchall():
            i = dict(zip(fields, i))
            try:
                i['ip'] = convert_ip(i['ip'])
            except ValueError:  # sometimes ip is None in wakaba db
                continue
            if i['reason'] is None:
                i['reason'] = ''
            yield i

    def get_table_posts(self, table):
        """Yields wakaba's post dict."""
        sql = 'SELECT * FROM {}{} ORDER BY num'
        self.cursor.execute(sql.format(self.prefix, table))
        fields = [i[0] for i in self.fields]
        for i in self.cursor.fetchall():
            p = dict(zip(fields, i))
            if p['subject'] is None:
                p['subject'] = ''
            if p['email'] is None:
                p['email'] = ''
            p['section_slug'] = table
            yield p

    def get_posts(self):
        for table in self.tables:
            for post in self.get_table_posts(table):
                yield post

    def convert_post(self, raw_post):
        """Converts wakaba's post dict to the chieftain WakabaPost object."""
        post = WakabaPost()
        post.section_slug = raw_post['section_slug']
        for t in self.fields:
            is_convertable = (len(t) == 3)
            if is_convertable:
                wfield, field, convert_fn = t
            else:
                wfield, field = t
            if field is None:
                continue
            # wakaba could have two different table schemas for different
            # board sections
            try:
                data = raw_post[wfield]
            except KeyError:
                continue
            if is_convertable:
                data = convert_fn(data)
            setattr(post, field, data)
        post.save()

    def convert(self):
        """Converts all wakaba post tables to chieftain WakabaPost table."""
        print 'Initializing wakaba bans'
        for i in self.get_bans():
            WakabaBan(**i).save()
        for i, p in enumerate(self.get_posts()):
            self.convert_post(p)
            print_flush('Initialized post {}'.format(i))
        print '\nInitialized {} posts. Trying to convert them...'.format(i)


class WakabaConverter(object):
    """Converts wakaba database to chieftain."""
    fields = (
        'pid', 'date', 'ip', 'poster', 'tripcode', 'email', 'topic',
        'password', 'message',
    )

    def __init__(self):
        super(WakabaConverter, self).__init__()
        self.section_map = dict(Section.objects.values_list('slug', 'id'))
        self.filetype_map = dict(FileType.objects.values_list('extension',
            'id'))
        self.thread_map = {}
        sl = WakabaPost.objects.distinct().values_list('section_slug')
        slugs = [i[0] for i in sl]
        self.bad_sections = {s for s in slugs if not self.section_map.get(s)}

    def convert_post(self, wpost, first_post=False):
        """Converts single post."""
        slug = wpost.section_slug
        if slug in self.bad_sections:
            raise ConvertError('Section {} does not exist'.format(slug))
        post = Post()
        post.data = ''
        for f in self.fields:
            setattr(post, f, getattr(wpost, f))
        # add video to the post
        if wpost.video:
            try:
                post.message += u' {}'.format(wpost.video)
            except UnicodeEncodeError:
                raise ConvertError('Cannot add video to the post {}'.format(
                    wpost.id))
        if first_post:
            post.is_op_post = True
            thread = Thread()
            thread.section_id = self.section_map[slug]
            for f in ('is_closed', 'is_pinned'):
                setattr(thread, f, getattr(wpost, f))
        else:
            tid = self.thread_map.get((slug, wpost.parent))
            try:
                thread = Thread.objects.get(id=tid)
            except Thread.DoesNotExist:
                raise ConvertError('Thread does not exist')
        thread.bump = wpost.date
        thread.save(rebuild_cache=False)
        if first_post:
            self.thread_map[(slug, wpost.pid)] = thread.id
        post.thread = thread

        if wpost.image:
            to = os.path.join(settings.WAKABA_PATH, slug)
            extension = wpost.image.split('.').pop()
            type_id = self.filetype_map.get(extension)
            if not type_id:
                raise ConvertError('Type {} does not exist'.format(extension))
            try:
                f = DjangoFile(open(os.path.join(to, wpost.image)))
            except IOError:
                pass
            else:
                file = File(
                    file=f, hash=wpost.image_md5, type_id=type_id,
                    image_width=wpost.image_width,
                    image_height=wpost.image_height
                )
                if wpost.thumb:
                    try:
                        thumb = DjangoFile(open(os.path.join(to, wpost.thumb)))
                    except IOError:
                        pass
                    else:
                        file.thumb = thumb
                if file.file:
                    file.save()
                    post.file = file
        post.save()
        thread.save()

    def convert_posts(self, start=0, first_post=False):
        filter_args = {'parent': 0} if first_post else {'parent__gt': 0}
        posts = WakabaPost.objects.filter(**filter_args).order_by('id')[start:]
        for i, p in enumerate(posts):
            i += start
            if first_post:
                i = 'f{}'.format(i)
            print_flush('Converting post {}'.format(i))
            try:
                self.convert_post(p, first_post)
            except ConvertError as e:
                print '\nFailed to convert post {}: {}'.format(i, e)
        print '\n'

    def convert_threads(self, start=0):
        return self.convert_posts(start, True)

    def convert_bans(self):
        print 'Converting bans'
        for ban in WakabaBan.objects.all():
            b = DeniedIP(ip=ban.ip, reason=ban.reason)
            b.by_id = 1
            b.save()

    def convert(self):
        self.convert_bans()
        self.convert_threads()
        self.convert_posts()
