#!/usr/bin/env python
# encoding: utf-8
"""
wakaba_convert.py

Created by Paul Bagwell on 2011-04-16.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from django.db import connection
from django.core.cache import cache
from django.core.management.base import BaseCommand
from board.models import Section, Post, Thread, File


class ConvertError(Exception):
    pass


class WakabaConverter(object):
    """Converts wakaba database to klipped.

    db_name -> thread.section
    timestamp -> post.date
    comment -> strip HTML
    password -> hash(password)
    parent -> if 0: create; thread_id
    name, trip, email, subject -> username, tripcode, email, topic
    ip -> normalize
    num -> pid
    image, width, height, thumbnail, md5 -> File
    """
    fields = (
        'num', 'parent', 'timestamp', 'lasthit', 'ip', 'date', 'name',
        'trip', 'email', 'subject', 'comment', 'image', 'size', 'md5',
        'width', 'height', 'thumbnail', 'tn_width', 'tn_height'
    )

    def __init__(self, connection, prefix='comments_'):
        self.prefix = prefix
        self.tables = [s.strip(prefix) for s in self.get_tables_list()]
        self.cursor = connection.cursor()

    def convert_post(self, wpost, table_name=''):
        """Converts post dict to klipped Post object."""
        new_thread = bool(wpost['parent'])
        has_file = bool(wpost['image'])
        post = Post()
        post.id = wpost['num']
        post.message = wpost['message'].striphtml()  # use django strip
        post.poster, post.tripcode = wpost['name'], wpost['trip']
        post.email = wpost['email']
        post.password = sha512(wpost['password'])
        post.ip = unpack(wpost['ip'], 'd')
        post.pid = wpost['num']

        if new_thread:
            section = Section.objects.get(slug=table_name)
            thread = Thread(section=section)
        else:  # TODO: make thread counter
            thread = Thread.objects.get(id)
        return post

    def get_table_data(self, table):
        sql = 'SELECT * FROM {0}{1}'.format(self.prefix, table)
        res = self.cursor.execute(sql)
        return (dict(zip(self.fields, c)) for c in res.fetchall())

    def convert(self):
        for table in self.tables:
            for post in self.get_table_data(table):
                p = self.convert_post(post, table)
                p.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        prefix = args[0] if len(args) > 0 else 'comments_'
        w = WakabaConverter(connection, prefix)
        w.convert()
