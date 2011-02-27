#!/usr/bin/env python
# encoding: utf-8
"""
comet.py

Created by Paul Bagwell on 2011-02-24.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""

import logging
import tornado.ioloop
import tornado.options
import tornado.web
import json
from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/api/stream/(\d+)/publish', MessageNewHandler),
            (r'/api/stream/(\d+)/subscribe', MessageUpdatesHandler),
        ]
        tornado.web.Application.__init__(self, handlers)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        json.dumps(MessageMixin.cache)


class MessageMixin(object):
    waiters = {}
    cache = {}
    cache_size = 200

    def wait_for_messages(self, callback, cursor=None):
        cls = MessageMixin
        t = self.thread_id
        if not self.cache.get(t):
            self.cache[t] = []
        if not self.waiters.get(t):
            self.waiters[t] = []
        cache = self.cache[t]
        waiters = self.waiters[t]

        if cursor:
            index = 0
            for i in xrange(len(cache)):
                index = len(cache) - i - 1
                if cache[index]['id'] == cursor:
                    break
            recent = cache[index + 1:]
            if recent:
                callback(recent)
                return None
        waiters.append(callback)

    def new_messages(self, posts):
        cls = MessageMixin
        t = self.thread_id
        if not self.cache.get(t):
            self.cache[t] = []
        if not self.waiters.get(t):
            self.waiters[t] = []
        cache = self.cache[t]
        waiters = self.waiters[t]

        for callback in waiters:
            try:
                callback(posts)
            except Exception:
                logging.error('Error in waiter callback', exc_info=True)
        waiters = []
        cache.extend(posts)
        if len(cache) > self.cache_size:
            cache = cache[-self.cache_size:]


class MessageNewHandler(MainHandler, MessageMixin):
    def post(self, thread_id):
        self.thread_id = thread_id
        post = self.get_argument('html')
        if self.get_argument('next', None):
            self.redirect(self.get_argument('next'))
        else:
            self.write(post)
        self.new_messages([post])


class MessageUpdatesHandler(MainHandler, MessageMixin):
    @tornado.web.asynchronous
    def post(self, thread_id):
        self.thread_id = thread_id
        self.wait_for_messages(self.async_callback(self.on_new_messages),
            cursor=self.get_argument('cursor', None))

    def on_new_messages(self, posts):
        # Closed client connection
        if self.request.connection.stream.closed():
            return None
        self.finish({'posts': posts})


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
