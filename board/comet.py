#!/usr/bin/env python
# encoding: utf-8
"""
comet.py

Created by Paul Bagwell on 2011-02-24.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""

import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self, pitux):
        self.write('Hey! {0}'.format(pitux))

application = tornado.web.Application([
    (r'/(\d+)', MainHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
