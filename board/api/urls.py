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
from board.api.handlers import PostHandler

post_handler = Resource(PostHandler)

urlpatterns = patterns('',
    (r'^post/(?P<id>\d+)$', post_handler),
    (r'^post/(?P<section>\w+)/(?P<pid>\d+)', post_handler),
)


# /api/post/