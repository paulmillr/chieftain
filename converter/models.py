#!/usr/bin/env python
# encoding: utf-8
"""
models.py

Created by Paul Bagwell on 2011-04-25.
Copyright (c) 2011 Paul Bagwell. All rights reserved.


w = WakabaConverter()
w.convert()
"""
import os
import re
import sys
from datetime import datetime
from struct import pack, unpack
from django.conf import settings
from django.core.files import File as DjangoFile
from django.db import models, connections, transaction
from django.utils.html import strip_tags as strip_html_tags
from board.models import Thread, Post, File, Section
from board.tools import get_key


class ConvertError(Exception):
    pass


def convert_ip(ip):
    """Converts IP from wakaba format to its normal string representation.
    Wakaba packs ip to the long integer with perl's pack() function.
    """
    try:
        adr = unpack('4B', pack('>L', int(ip)))  # 4-tuple
    except Exception as e:
        raise ValueError(e)
    return '.'.join(str(i) for i in adr)

SUBST_MAP = (
    (r'<strong>(.*)</strong>', r'**\1**'),
    (r'<em>(.*)</em>', r'*\1*'),
    (r'&gt;', '>'),
    (r'>>(\d{1,10})</a>', r'>>\1</a>'),
    (r'<br />', '\n'),
    (r'<span class="unkfunc">>(.*)</span>', r'>\1'),
    (r'<span class="spoiler">(.*)</span>', r'%%\1%%'),
)
SUBST_MAP = [(re.compile(r), s) for r, s in SUBST_MAP]

def strip_tags(text, allowed_tags=[]):
    for r, s in SUBST_MAP:
        text = re.sub(r, s, text)
    return strip_html_tags(text)


def print_flush(text):
    sys.stdout.write('\r' + text)
    sys.stdout.flush()


class WakabaPost(models.Model):
    """Used as temporary storage of wakaba posts on database convertation.
    This model represents wakaba post with some additions, like:
    - section slug (wakaba doesn't have sections)
    - some fields renamed (num -> pid, trip -> tripcode) to match klipped style
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


class WakabaInitializer(object):
    """Copies posts from all wakaba databases to one big temporary db.

    Initializer contains 'fields' field (2 or 3-tuple), that determines
    convertable fields in format:
    * wakaba field name
    * klipped field name in the temporary model
    * convert function (optional)
    Also if klipped field name is None, it won't be converted.
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

    def get_table_posts(self, table):
        """Yields wakaba's post dict."""
        sql = 'SELECT * FROM {0}{1} ORDER BY num'
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
        """Converts wakaba's post dict to the klipped WakabaPost object."""
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
            data = raw_post[wfield]
            if is_convertable:
                data = convert_fn(data)
            setattr(post, field, data)
        post.save()

    def convert(self):
        """Converts all wakaba post tables to one klipped WakabaPost table."""
        for i, p in enumerate(self.get_posts()):
            self.convert_post(p)
            print_flush('Converted post {0}'.format(i))
        print 'Initialized {0} posts. Trying to convert them...'.format(i)


class WakabaConverter(object):
    """Converts wakaba database to klipped."""
    fields = (
        'pid', 'date', 'ip', 'poster', 'tripcode', 'email', 'topic',
        'password', 'message'
    )

    def __init__(self):
        super(WakabaConverter, self).__init__()
        self.section_map = dict(Section.objects.values_list('slug', 'id'))
        ss = WakabaPost.objects.distinct().values_list('section_slug')
        sections = [i[0] for i in ss]
        self.bad_sections = {
            s for s in sections if not self.section_map.get(s)
        }
        self.thread_map = {}
        #self.thread_map = self.build_thread_map()

    def build_thread_map(self):
        thread_ids = (i[0] for i in Thread.objects.values_list('id'))
        wpost_ids = (i[0] for i in
            WakabaPost.objects.filter(parent=0).values_list('id'))
        return dict(zip(thread_ids, wpost_ids))

    def convert_post(self, wpost, first_post=False):
        """Converts single post."""
        if wpost.section_slug in self.bad_sections:
            return False
        post = Post()
        post.data = ''
        for f in self.fields:
            setattr(post, f, getattr(wpost, f))
        if first_post:
            post.is_op_post = True
            thread = Thread()
            thread.section_id = self.section_map[wpost.section_slug]
        else:
            key = '{0}_{1}'.format(wpost.section_slug, wpost.parent)
            tid = self.thread_map.get(key)
            try:
                thread = Thread.objects.get(id=tid)
            except Thread.DoesNotExist:
                print '\nFailed to convert post {0}'.format(wpost.id)
                return False
        thread.bump = wpost.date
        thread.save(rebuild_cache=False)
        if first_post:
            key = '{0}_{1}'.format(wpost.section_slug, wpost.pid)
            self.thread_map[key] = thread.id
        post.thread = thread

        if wpost.image:  # TODO
            img = os.path.join(WAKABA_PATH, wpost.image)
            file = File(
                file=DjangoFile(img), hash=wpost.image_md5,
                image_width=wpost.image_width, image_height=wpost.image_height
            )
            if wpost.thumb:
                thumb = os.path.join(WAKABA_PATH, wpost.thumb)
                file.thumb = DjangoFile(wpost.thumb)
            file.save()
            post.file = file
        post.save()
        thread.save()

    @transaction.commit_manually
    def convert_threads(self):
        first_posts = WakabaPost.objects.filter(parent=0).order_by('id')
        for i, p in enumerate(first_posts):
            print_flush('Converted first post {0}'.format(i))
            self.convert_post(p, True)
            if i % 1000 == 0:
                transaction.commit()
        transaction.commit()
        print

    @transaction.commit_manually
    def convert_posts(self):
        posts = WakabaPost.objects.filter(parent__gt=0).order_by('id')
        for i, p in enumerate(posts):
            print_flush('Converted post {0}'.format(i))
            self.convert_post(p)
            if i % 1000 == 0:
                transaction.commit()
        transaction.commit()
        print

    def convert(self):
        self.convert_threads()
        self.convert_posts()
