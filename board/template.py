#!/usr/bin/env python
# encoding: utf-8
"""
template.py

Created by Paul Bagwell on 2011-02-22.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""

import os
import codecs
import shutil
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from board.shortcuts import rtr

__all__ = ['render_to_file', 'handle_file_cache', 'rebuild_cache']


def render_to_file(template, filename, request, context):
    with codecs.open(filename, 'w', 'utf-8') as f:
        f.write(render_to_string(template, context, RequestContext(request)))


def handle_file_cache(template, filename, request, context):
    if context.get('mod'):
        return rtr(template, request, context, True)
    filename = os.path.join('cache', *filename.split('/'))
    if not os.path.exists(filename):
        d = os.path.dirname(filename)
        if not os.path.isdir(d):
            os.makedirs(d)
        render_to_file(template, filename, request, context)
    try:
        with open(filename) as f:
            return HttpResponse(f.read())
    except IOError:
        return rtr(template, request, context, True)


def rebuild_cache(section_slug, item):
    """Refresh cache of:

       * thread/item.html
       * threads.html*
       * posts/*
       * page/*

       Can take iterable as second argument.
    """
    pathes = ['page/', 'posts/', 'threads.html']
    if hasattr(item, '__iter__'):
        for i in item:
            pathes.append('thread/{0}.html'.format(i))
    else:
        pathes.append('thread/{0}.html'.format(item))
    for i in pathes:
        isdir = bool(i.endswith('/'))
        t = os.path.join('cache', section_slug, *i.split('/'))
        if os.path.exists(t):
            if not isdir:
                os.remove(t)
            else:
                shutil.rmtree(t)
