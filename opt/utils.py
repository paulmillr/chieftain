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
import urllib2
import sys
from board.models import *
from django.template.loader import render_to_string
from django.conf import settings
from django.core.cache import cache

__all__ = ['rebuild', 'wipe', 'clear', 'generate']


def rebuild():
    """Rebuilds cache."""
    shutil.rmtree('cache', ignore_errors=True)
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


def wipe(posts=10, thread_or_slug='', domain='http://b.2-ch.ru/'):
    """Requires Python 3.2."""
    # >>> wipe(50000, 'b')
    # 50000 posts in 0:34:54.923063

    if sys.version_info[0] < 3:
        raise Exception('You need Python 3.2+ to use this function.')
    import urllib.request
    import random
    import concurrent.futures
    from datetime import datetime
    start = datetime.now()
    uri = '{0}api/post/'.format(domain)

    def rand():
        return str(int(random.random() * 100000) % 50000)

    if thread_or_slug.isdigit():
        data = 'thread={0}'.format(thread_or_slug)
    else:
        data = 'section={0}'.format(thread_or_slug)
    data += '&poster=&email=&topic=&password=test&message=WIPE'
    opener = urllib.request.URLopener()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for i in range(posts):
            executor.submit(opener.open, uri, data + rand())
    print('{0} posts in {1}'.format(posts, datetime.now() - start))


def clear():
    """Clears board."""
    threads = Thread.objects.all().delete()
    posts = Post.objects.all().delete()
    files = File.objects.all().delete()
    cache.clear()
    make_path = lambda x: os.path.join(settings.MEDIA_ROOT, x)
    for d in [make_path(x) for x in ['section', 'thumbs']]:
        shutil.rmtree(d, ignore_errors=True)
    shutil.rmtree('cache', ignore_errors=True)
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
