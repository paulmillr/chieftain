#!/usr/bin/env python
# encoding: utf-8
"""
tools.py

Created by Paul Bagwell on 2011-01-30.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
import os
import re
import httpagentparser
import tempfile
import time
from PIL import Image
from django.core.files import File as DjangoFile
from hashlib import sha1
from string import maketrans
from crypt import crypt
from django.conf import settings
from datetime import datetime


__all__ = [
    'handle_uploaded_file', 'tripcode', 'key', 'parse_user_agent',
    'make_post_descriptions',
    'take_first', 'from_timestamp'
]


def handle_uploaded_file(file_instance):
    """Moves uploaded file to files directory and makes thumb."""
    def make_path(dir):
        return os.path.join(settings.MEDIA_ROOT, dir)
    f = file_instance
    directory = make_path('section')
    if not os.path.isdir(directory):
        os.makedirs(directory)
    f.save()
    try:  # make thumb
        img = Image.open(f.file.file)
        f.image_height, f.image_width = img.size
        MAX = 200
        if max(img.size) < MAX:
            f.save()
            return f
        thumb_dir = make_path('thumbs')
        if not os.path.isdir(thumb_dir):
            os.makedirs(thumb_dir)
        with tempfile.NamedTemporaryFile(
            suffix='.{0}'.format(f.type.extension)) as tmp:
            img.thumbnail((MAX, MAX), Image.ANTIALIAS)
            img.save(tmp)
            f.thumb = DjangoFile(tmp)
            f.save()
    except IOError:
        pass
    return f


def tripcode(text):
    """Makes tripcode from text."""
    text = text.replace('\\', '')
    trip = text.replace('#', '') if '##' in text else text
    trip = unicode(trip).encode('shift-jis')
    salt = trip + 'H.'
    salt = re.sub('/[^\.-z]/', '.', salt[1:3])
    salt = salt.translate(maketrans(':;<=>?@[\]^_`', 'ABCDEFGabcdef'))
    return crypt(trip, salt)[-10:]


def make_post_descriptions(posts):
    """Takes Post QuerySet and generates description to all posts."""
    posts = posts.values('thread__section__name', 'thread__section__slug',
        'pid', 'topic', 'message'
    )
    for post in posts:
        post['link'] = '/{slug}/{pid}'.format(
            slug=post['thread__section__slug'], pid=post['pid'])
        post['description'] = (post['topic'] or post['message'] or
            '>>{0}'.format(post['pid']))
        yield post


def key(text):
    """Generates key for passwords etc."""
    return sha1(text).hexdigest()


def parse_user_agent(user_agent):
    return httpagentparser.detect(user_agent)


def take_first(list):
    """Returns first elements of list."""
    return [i[0] for i in list]


def from_timestamp(timestamp):
    """Convert timestamp to datetime object."""
    return str(datetime.fromtimestamp(int(timestamp)))


def timestamp_now():
    return int(time.time() * 100)
