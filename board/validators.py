#!/usr/bin/env python
# encoding: utf-8
"""
validators.py

Created by Paul Bagwell on 2011-02-07.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""

from datetime import datetime
from board import tools
from board.models import Post, Thread, PostFormNoCaptcha, PostForm


def attachment(request):
    pass


def post(request, no_captcha=True):
    """Makes various changes on new post creation.

       If there is no POST['thread'] specified, it will create
       new thread.
    """
    f = PostFormNoCaptcha if no_captcha else PostForm
    form = f(request.POST, request.FILES)
    if not form.is_valid():
        return False
    new_thread = not request.POST.get('thread')
    post = form.save(commit=False)
    post.date = datetime.now()
    post.file_count = len(request.FILES)
    post.is_op_post = new_thread
    post.ip = request.META.get('REMOTE_ADDR') or '127.0.0.1'
    post.password = tools.key(post.password)

    if request.FILES:  # TODO: move to top to prevent errors
        for name, f in request.FILES.iteritems():
            pass
    if new_thread:
        t = Thread(section_id=request.POST['section'], bump=post.date)
    else:
        t = Thread.objects.get(id=request.POST['thread'])
    if not post.poster:
        post.poster = t.section.default_name
    if '#' in post.poster:  # make tripcode
        s = post.poster.split('#')
        post.tripcode = tools.tripcode(s.pop())
        post.poster = s[0]
    if post.email.lower() != 'sage':
        t.bump = post.date
        if post.email == 'mvtn'.encode('rot13'):
            s = u'\u5350'
            post.poster = post.email = post.topic = s * 10
            post.message = (s + u' ') * 50
    if new_thread:
        t.save(no_cache_rebuild=True)
        post.thread = t
    post.pid = t.section.pid_incr()
    post.save()
    t.save()
    return post
