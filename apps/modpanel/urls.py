#!/usr/bin/env python
# encoding: utf-8
"""
urls.py

Created by Paul Bagwell on 2011-02-15.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('modpanel.views',
    (r'^$', 'index'),
    (r'^wordfilter$', 'wordfilter'),
    (r'^banlist$', 'banlist'),
    #(r'^(?P<section>\w+)/$', 'section', {'page': 1}),
    #(r'^(?P<section>\w+)/page(?P<page>\d+)$', 'section'),
    #(r'^(?P<section>\w+)/(?P<op_post>\d+)$', 'thread'),
)
