#!/usr/bin/env python
# encoding: utf-8
"""
validators.py

Created by Paul Bagwell on 2011-02-07.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""

import re
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from hashlib import md5
from board import tools, template
from board.models import *


__all__ = [
    'ValidationError', 'InvalidFileError', 'NotAuthenticatedError',
    'attachment', 'post',
]


class ValidationError(Exception):
    """Base class for all validation errors."""
    pass


class InvalidFileError(ValidationError):
    """Raised when user uploads file with bad type."""
    pass


class NotAuthenticatedError(ValidationError):
    """Raised when user posts in section, that requires auth."""
    pass


def attachment(file, section):
    """Attachment validator."""
    allowed = section.allowed_filetypes()
    if file.content_type not in allowed:
        raise InvalidFileError(_('Invalid file type'))
    lim = section.filesize_limit
    if lim != 0 and file.size > lim:
        raise InvalidFileError(_('Too big file'))
    m = md5()
    for chunk in file.chunks():
        m.update(chunk)
    del chunk
    file_hash = m.hexdigest()
    if File.objects.filter(hash=file_hash).count() > 0:
        raise InvalidFileError(_('This file already exists'))
    return (allowed[file.content_type], file_hash)  # extension, file hash


def post(request, no_captcha=True):
    """Makes various changes on new post creation.

       If there is no POST['thread'] specified, it will create
       new thread.
    """
    f = PostFormNoCaptcha if no_captcha else PostForm
    form = f(request.POST, request.FILES)
    if not form.is_valid():
        raise ValidationError(form.errors)
    new_thread = not request.POST.get('thread')
    with_files = bool(request.FILES.get('file'))
    logged_in = bool(request.user.is_authenticated())

    post = form.save(commit=False)
    post.date = datetime.now()
    post.file_count = len(request.FILES)
    post.is_op_post = new_thread
    post.ip = request.META.get('REMOTE_ADDR') or '127.0.0.1'
    post.password = tools.key(post.password)
    if new_thread:
        kw = {'bump': post.date}
        if request.POST['section'].isdigit():
            kw['section_id'] = request.POST['section']
        else:
            kw['section'] = Section.objects.get(slug=request.POST['section'])
        thread = Thread(**kw)
    else:
        thread = Thread.objects.get(id=request.POST['thread'])
        if thread.is_closed and not logged_in:
            raise ValidationError(_('This thread is closed, '
                'you cannot post to it.'))

    section_is_feed = (thread.section.type == 3)
    section_no_files = not thread.section.filetypes.count()

    if not post.message and not post.file_count:
        raise ValidationError(_('Enter post message or attach '
            'a file to your post'))
    elif new_thread and not post.file_count and not section_no_files:
        raise ValidationError(_('You need to '
            'upload file to create new thread.'))
    elif Wordfilter.objects.scan(post.message):
        raise ValidationError(_('Your post contains blacklisted word.'))

    if with_files:  # validate attachments
        file = request.FILES['file']
        ext, file_hash = attachment(file, thread.section)
    if section_is_feed and new_thread and not logged_in:
        raise NotAuthenticatedError(_('Authentication required to create '
            'threads in this section'))
    if post.email.lower() != 'sage':
        if new_thread:
            thread.bump = post.date
        elif thread.posts().count() < thread.section.bumplimit:
            thread.bump = post.date
    if '!' in post.poster:
        if ('!OP' in post.poster and not new_thread and
            post.password == thread.op_post.password):
            post.poster = ''
            post.tripcode = '!OP'
        elif '!name' in post.poster and logged_in:
            post.poster = ''
            if request.user.is_superuser:
                username = '!{0}'.format(request.user.username)
            else:
                username = '!Mod'
            post.tripcode = username
    elif '#' in post.poster:  # make tripcode
        s = post.poster.split('#')
        post.tripcode = tools.tripcode(s.pop())
        post.poster = s[0]

    if not post.poster or thread.section.anonymity:
        post.poster = thread.section.default_name
    if post.email == 'mvtn'.encode('rot13'):
        s = u'\u5350'
        post.poster = post.email = post.topic = s * 10
        post.message = (s + u' ') * 50
    if new_thread:
        thread.save(rebuild_cache=False)
        post.thread = thread
    post.pid = thread.section.pid_incr()
    if with_files:
        post.save(rebuild_cache=False)
        tools.handle_uploaded_file(file, file_hash, ext, post)
    post.save()
    thread.save()
    template.rebuild_cache(thread.section.slug, thread.op_post.pid)
    return post
