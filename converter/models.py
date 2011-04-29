#!/usr/bin/env python
# encoding: utf-8
"""
models.py

Created by Paul Bagwell on 2011-04-25.
Copyright (c) 2011 Paul Bagwell. All rights reserved.


w = WakabaConverter()
w.convert()
"""
import sys
from datetime import datetime
from struct import pack, unpack
from django.db import models, connections
from django.utils.html import strip_tags
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
            data = raw_post[wfield]
            if is_convertable:
                data = convert_fn(data)
            elif field is None:
                continue
            setattr(post, field, data)
        post.save()

    def convert(self):
        """Converts all wakaba post tables to one klipped WakabaPost table."""
        for i, p in enumerate(self.get_posts()):
            self.convert_post(p)
            print_flush('Converted post {0}'.format(i))


class WakabaConverter(object):
    """Converts wakaba database to klipped."""
    fields = (
        'pid', 'date', 'ip', 'poster', 'tripcode', 'email', 'topic',
        'password', 'message'
    )

    def __init__(self):
        super(WakabaConverter, self).__init__()
        self.section_map = dict(Section.objects.values_list('slug', 'id'))
        self.thread_map = {}

    def convert_post(self, wpost, first_post=False):
        """Converts single post."""
        post = Post()
        for f in self.fields:
            setattr(post, f, getattr(wpost, f))
        if first_post:
            thread = Thread()
            try:
                s = wpost.section_slug
                section = self.section_map[s]
            except KeyError:
                raise ConvertError('Board section "{0}" does not exist'.format(
                    s))
            thread.section_id = section
        else:
            tid = self.thread_map.get(wpost.parent)
            thread = Thread.objects.get(id=tid)

        thread.bump = wpost.date
        thread.save()
        if first_post:
            self.thread_map[wpost.parent] = thread.id
        post.thread = thread

        if wpost.image and False:  # TODO
            f = File()
            f.size = wpost.image_size
            f.hash = wpost.image_md5
            f.image_width = wpost.image_width
            f.image_height = wpost.image_height
            #if post.thumb:
            #    f.thumb = post.thumb
            f.save()
            post.file = f
        post.save()

    def convert(self):
        first_posts = WakabaPost.objects.filter(parent=0)
        posts = WakabaPost.objects.filter(parent__gt=0)
        for i, p in enumerate(first_posts):
            print_flush('Converted first post {0}'.format(i))
            self.convert_post(p, True)
        for i, p in enumerate(posts):
            print_flush('Converted post {0}'.format(i))
            self.convert_post(p)
