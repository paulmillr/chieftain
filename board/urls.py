#!/usr/bin/env python
# encoding: utf-8
"""
urls.py

Created by Paul Bagwell on 2011-01-13.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('board.views',
    (r'^$', 'index'),
    (r'^settings$', 'settings'),
    (r'^faq$', 'faq'),
    (r'^search/$', 'search'),
    (r'^(?P<section>\w+)/$', 'section', {'page': 1}),
    (r'^(?P<section>\w+)/page(?P<page>\d+)$', 'section'),
    (r'^(?P<section>\w+)/(?P<op_post>\d+)$', 'thread'),
)

#urlpatterns += patterns('board.comet',
#    (r'^comet/thread/(?P<thread_id>\d+)', 'thread'),
    #(r'^comet/section/(?P<section)' 'section'),
    #(r'^comet/user/(?P<session>\w+)', 'user'),
#)