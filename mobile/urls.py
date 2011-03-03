#!/usr/bin/env python
# encoding: utf-8
"""
urls.py

Created by Paul Bagwell on 2011-03-02.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('mobile.views',
    (r'^$', 'index'),
    (r'^(?P<section_slug>\w+)/$', 'section', {'page': 1}),
    (r'^(?P<section_slug>\w+)/page(?P<page>\d+)$', 'section'),
    (r'^(?P<section_slug>\w+)/(?P<op_post>\d+)$', 'thread'),
)
