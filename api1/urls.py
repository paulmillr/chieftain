#!/usr/bin/env python
# encoding: utf-8
"""
urls.py

Created by Paul Bagwell on 2011-01-28.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from django.conf.urls.defaults import patterns
from api1.views import *


urlpatterns = patterns('api1.views',
    (r'^$', 'api'),
    # user settings
    (r'^setting/$', SettingRootResource.as_view()),
    (r'^setting/(?P<key>[\w\d]+)$', SettingResource.as_view()),
    (r'^feed/$', FeedRootResource.as_view()),
    (r'^feed/(?P<key>[\d]+)$', FeedResource.as_view()),
    (r'^hidden/$', HideRootResource.as_view()),
    (r'^hidden/(?P<key>[\d]+)?$', HideResource.as_view()),
    # polls
    (r'^poll/$', PollRootResource.as_view()),
    (r'^poll/(?P<id>\d+)$', PollResource.as_view()),
    (r'^choice/$', ChoiceRootResource.as_view()),
    (r'^choice/(?P<id>\d+)$', ChoiceResource.as_view()),
    (r'^vote/$', VoteRootResource.as_view()),
    (r'^vote/(?P<id>\d+)', VoteResource.as_view()),
    # list of threads with all their posts
    (r'^thread/$', ThreadRootResource.as_view()),
    (r'^thread/(?P<section__slug>\w+)/$', ThreadRootResource.as_view()),
    # single threads
    (r'^thread/(?P<id>\d+)$', ThreadResource.as_view()),
    # by first post pid
    (r'^thread/(?P<section__slug>\w+)/(?P<id>\d+)$',
        ThreadResource.as_view()),
    # list of posts
    (r'^post/$', PostRootResource.as_view()),
    (r'^post/(?P<thread__section__slug>\w+)/$', PostRootResource.as_view()),
    (r'^post/(?P<thread__section__slug>\w+)/first/$',
        PostRootResource.as_view(), {'is_op_post': True}),
    # single posts
    (r'^post/(?P<id>\d+)$', PostResource.as_view()),
    (r'^post/(?P<thread__section__slug>\w+)/(?P<pid>\d+)$',
        PostResource.as_view()),
    (r'^section/$', SectionRootResource.as_view()),
    (r'^section/(?P<id>\d+)$', SectionResource.as_view()),
    (r'^section/(?P<slug>\w+)', SectionResource.as_view()),
    (r'^sectiongroup/', SectionGroupRootResource.as_view()),
    (r'^sectiongroup/(?P<id>\d+)', SectionGroupResource.as_view()),
    (r'^file/$', FileRootResource.as_view()),
    (r'^file/random_image/(?P<count>\d{1,2})',
        RandomImageRootResource.as_view()),
    (r'^file/(?P<id>\d+)$', FileResource.as_view()),
    (r'^filetype/$', FileTypeRootResource.as_view()),
    (r'^filetype/(?P<id>\d+)$', FileTypeResource.as_view()),
    (r'^filetype/(?P<extension>[\w\d]+)$', FileTypeResource.as_view()),
    (r'^filetypegroup/$', FileTypeGroupRootResource.as_view()),
    (r'^filetypegroup/(?P<id>\d+)$', FileTypeGroupResource.as_view()),
)
