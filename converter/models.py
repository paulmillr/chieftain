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
from board.tools import get_key


def convert_ip(ip):
    """By default, Wakaba packs ip to the integer with perl's pack()
    function.
    """
    adr = unpack('4B', pack('>L', int(ip)))  # 4-tuple
    return '.'.join(str(i) for i in adr)


class WakabaPost(models.Model):
    pid = models.IntegerField()
    section = models.CharField(max_length=10)
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
    image_size = models.IntegerField(null=True)
    image_md5 = models.TextField(null=True)
    image_width = models.IntegerField(null=True)
    image_height = models.IntegerField(null=True)
    thumbnail = models.TextField(null=True)


class WakabaConverter(object):
    """Converts wakaba database to klipped."""
    fields = (
        ('num', 'pid'),
        ('parent', 'parent'),
        ('timestamp', 'date', lambda f: datetime.fromtimestamp(float(f))),
        ('lasthit', None),
        ('ip', 'ip', lambda f: convert_ip(f)),
        ('date', None),
        ('name', 'poster'),
        ('trip', 'tripcode', lambda f: f.strip('!')),
        ('email', 'email'),
        ('subject', 'topic'),
        ('password', 'password', lambda f: get_key(f)),
        ('comment', 'message', lambda f: strip_tags(f)),
        ('image', 'image'),
        ('size', 'image_size'),
        ('md5', 'image_md5'),
        ('width', 'image_width'),
        ('height', 'image_height'),
        ('thumbnail', 'thumb'),
        ('tn_width', None),
        ('tn_height', None),
    )

    def __init__(self, prefix='comments_'):
        self.prefix = prefix
        self.cursor = connections['wakaba'].cursor()
        self.threads_map = {}
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
            p['section'] = table
            yield p

    def convert_post(self, raw_post):
        """Converts wakaba's post dict to the klipped WakabaPost object."""
        post = WakabaPost()
        post.section = raw_post['section']
        for t in self.fields:
            convertable = (len(t) == 3)
            if convertable:
                wfield, field, convert_fn = t
            else:
                wfield, field = t
            data = raw_post[wfield]
            if convertable:
                data = convert_fn(data)
            elif field is None:
                continue
            setattr(post, field, data)
        post.save()

    def convert(self):
        """Converts all wakaba post tables to one klipped WakabaPost table."""
        pid = 0
        for t in self.tables:
            posts = self.get_table_posts(t)
            for post in posts:
                pid += 1
                sys.stdout.write('\rConverted post {0}'.format(pid))
                sys.stdout.flush()
                self.convert_post(post)
