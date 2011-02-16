#!/usr/bin/env python
# encoding: utf-8
"""
comet.py

Created by Paul Bagwell on 2011-02-15.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""

import gevent
import geventmysql
import json
from django.http import HttpResponse
from django.conf import settings

__all__ = ['gev']


class GeventDB(object):
    """Wrapper around geventmysql."""
    def __init__(self, settings):
        d = settings.DATABASES.items().pop()[1]
        host, user, paswd = d['HOST'] or '127.0.0.1', d['USER'], d['PASSWORD']
        conn = geventmysql.connect(host=host, user=user, password=paswd,
            charset='utf8')
        cur = conn.cursor()
        cur.execute('USE {0}'.format(d['NAME']))
        cur.execute('SET NAMES "utf8"')
        self.conn = conn
        self.cur = cur

    def pull(self, thread_id):
        """Pulls thread html."""
        s = 'SELECT html FROM board_post WHERE thread_id = "{0}"'
        self.cur.execute(s.format(thread_id))
        return [i[0] for i in self.cur.fetchall()]


def json_response(value, **kwargs):
    kwargs.setdefault('content_type', 'text/javascript; charset=UTF-8')
    return HttpResponse(json.dumps(value), **kwargs)


class ThreadRoom(object):
    """Comet thread 'chat' room."""
    def __init__(self, arg):
        self.new_message_event = gevent.event.Event()
        self.db = GeventDB(settings)
        self.cache = []

    def message_new(self, msg):
        """Adds new message to the cache and sends event.

           msg - html cache of the post
        """
        self.cache.append(msg)
        if len(self.cache) > self.cache_size:
            self.cache = self.cache[-self.cache_size:]
        self.new_message_event.set()
        self.new_message_event.clear()
        return json_response(msg)

    def message_updates(self, request, thread):
        r = request.session.get('cursor') or {}
        cursor = r.get(thread)
        print 'CURSOR'
        print repr(cursor)
        print 'CACHE'
        print repr(self.cache)
        if not self.cache or cursor == self.cache[-1]['id']:
            self.new_message_event.wait()
        assert cursor != self.cache[1]['id'], cursor
        try:
            for index, m in enumerate(self.cache):
                if m['id'] == cursor:
                    return json_response({'messages': self.cache[index + 1:]})
            return json_response({'messages': self.cache})
        finally:
            if self.cache:
                request.session['cursor'][thread] = self.cache[-1]['id']
            else:
                request.session['cursor'].pop(thread, None)


t = ThreadRoom()
thread = t.message_updates
