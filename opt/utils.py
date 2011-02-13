#!/usr/bin/env python
# encoding: utf-8
"""
utils.py

Created by Paul Bagwell on 2011-01-22.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
import glob
import os
import shutil
from board.models import *
from django.template.loader import render_to_string
from django.conf import settings

__all__ = ['rebuild', 'generate']


def rebuild():
    """Rebuilds cache."""
    threads = Thread.objects.all()
    posts = Post.objects.all()
    for c, tr in enumerate(threads):
        tr.save()
        if c % 50 == 0:
            print 'Rendered thread {0}'.format(c)

    for c, post in enumerate(posts):
        post.save()
        if c % 250 == 0:
            print 'Rendered post {0}'.format(c)


def wipe():
    """Wipes board."""
    from django.core.cache import cache
    threads = Thread.objects.all().delete()
    posts = Post.objects.all().delete()
    files = File.objects.all().delete()
    cache.clear()
    make_path = lambda x: os.path.join(settings.MEDIA_ROOT, x)
    for d in [make_path(x) for x in ['section', 'thumbs']]:
        shutil.rmtree(d, ignore_errors=True)
    return True


def generate(section='au', threads=100, posts=200):
    """Generates content for imageboard."""
    sect = Section.objects.get(slug__exact=section)
    c = 0
    for t in range(1, threads):
        if t < 10:
            time = '0{}'.format(t)
        else:
            if t > 99:
                time = 99
            else:
                time = t
        targs = {
            'bump': '20{0!s}-01-20 14:12:13'.format(time),
            'section': sect,
        }
        tr = Thread(**targs)
        tr.save()
        for p in range(1, posts):
            c += 1
            print c
            iop = 1 if p == 1 else 0
            args = {
                'pid': c,
                'thread': tr,
                'is_op_post': iop,
                'ip': '127.{0!s}.{1!s}.1'.format(t, p),
                'topic': 'Thread {0!s}, post {1!s}'.format(t, p),
                'message': 'Hi, guyz! It is threadpost {0!s}'.format(t * p),
            }
            post = Post(**args)
            post.save()
        tr.html = render_to_string('thread.html', {'thread': tr})
        tr.save()
