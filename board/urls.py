#!/usr/bin/env python
# encoding: utf-8
"""
urls.py

Created by Paul Bagwell on 2011-01-13.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from django.conf.urls.defaults import patterns
from board.models import SectionFeed, ThreadFeed

urlpatterns = patterns('board.views',
    (r'^$', 'index'),
    (r'^settings$', 'settings'),
    (r'^faq$', 'faq'),
    (r'^feed$', 'storage', {'name': 'feed'}),
    (r'^search/$', 'search'),
    (r'^(?P<section_slug>\w+)/$', 'section', {'page': 1}),
    (r'^(?P<section_slug>\w+)/page(?P<page>\d+)$', 'section'),
    (r'^(?P<section_slug>\w+)/threads$', 'threads'),
    (r'^(?P<section_slug>\w+)/rss$', SectionFeed()),
    (r'^(?P<section_slug>\w+)/search$', 'search', {'page': 1}),
    (r'^(?P<section_slug>\w+)/(?P<op_post>\d+)$', 'thread'),
    (r'^(?P<section_slug>\w+)/(?P<op_post>\d+)/rss', ThreadFeed()),
)
