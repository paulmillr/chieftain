#!/usr/bin/env python
# encoding: utf-8
"""
urls.py

Created by Paul Bagwell on 2011-01-28.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from django.conf.urls.defaults import *
from django.contrib import admin
from piston.resource import Resource
from board.api.handlers import *

post_handler = Resource(PostHandler)
thread_handler = Resource(ThreadHandler)
section_handler = Resource(SectionHandler)
section_group_handler = Resource(SectionGroupHandler)
filetype_handler = Resource(FileTypeHandler)
file_category_handler = Resource(FileCategoryHandler)
user_handler = Resource(UserHandler)

urlpatterns = patterns('',
    (r'^post/$', post_handler),
    (r'^post/(?P<id>\d+)$', post_handler),
    (r'^post/(?P<section>\w+)/$', post_handler),
    (r'^post/(?P<section>\w+)/(?P<pid>\d+)$', post_handler),
    (r'^thread/$', thread_handler),
    (r'^thread/(?P<id>\d+)$', thread_handler),
    (r'^thread/(?P<section>\w+)$', thread_handler),
    (r'^thread/(?P<section>\w+)/(?P<page>\d+)$', thread_handler),
    (r'^thread/(?P<section>\w+)/(?P<op_post>\d+)$', thread_handler),
    (r'^section/$', section_handler),
    (r'^section/group/', section_group_handler),
    (r'^section/group/(?P<id>\d+)', section_group_handler),
    (r'^section/(?P<id>\d+)$', section_handler),
    (r'^section/(?P<slug>\w+)', section_handler),
    (r'^filetype/$', filetype_handler),
    (r'^filetype/(?P<id>\d+)$', filetype_handler),
    (r'^filecategory/$', file_category_handler),
    (r'^filecategory/(?P<id>\d+)$', file_category_handler),
    (r'^user/$', user_handler),
    (r'^user/(?P<id>\d+)$', user_handler),
)
