#!/usr/bin/env python
# encoding: utf-8
"""
urls.py

Created by Paul Bagwell on 2011-01-28.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from django.conf.urls.defaults import patterns

urlpatterns = patterns('board.api.resources',
    (r'^post/$', 'PostRootResource'),
    (r'^post/(?P<id>\d+)$', 'PostResource'),
    # TODO: Optimize this!
    (r'^post/(?P<thread__section__slug>\w+)/$', 'PostResource'),
    (r'^post/(?P<thread__section__slug>\w+)/(?P<pid>\d+)$', 'PostResource'),
    (r'^thread/$', 'ThreadRootResource'),
    (r'^thread/(?P<id>\d+)$', 'ThreadResource'),
    (r'^thread/(?P<section__slug>\w+)$', 'ThreadResource'),
    (r'^thread/(?P<section__slug>\w+)/(?P<page>\d+)$', 'ThreadResource'),
    (r'^thread/(?P<section__slug>\w+)/(?P<op_post>\d+)$', 'ThreadResource'),
    (r'^section/$', 'SectionRootResource'),
    (r'^section/group/', 'SectionGroupRootResource'),
    (r'^section/group/(?P<id>\d+)', 'SectionGroupResource'),
    (r'^section/(?P<id>\d+)$', 'SectionResource'),
    (r'^section/(?P<slug>\w+)', 'SectionResource'),
    (r'^file/$', 'FileRootResource'),
    (r'^file/(?P<id>\d+)$', 'FileResource'),
    (r'^filetype/$', 'FileTypeRootResource'),
    (r'^filetype/(?P<id>\d+)$', 'FileTypeResource'),
    (r'^filetypegroup/$', 'FileTypeGroupRootResource'),
    (r'^filetypegroup/(?P<id>\d+)$', 'FileTypeGroupResource'),
)
