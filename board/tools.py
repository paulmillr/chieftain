#!/usr/bin/env python
# encoding: utf-8
"""
tools.py

Created by Paul Bagwell on 2011-01-30.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
import os
import re
import tempfile
from PIL import Image
from django.core.files import File as DjangoFile
from hashlib import md5, sha256
from string import maketrans
from crypt import crypt
from klipped import settings
from datetime import datetime
from board.models import File, FileType

__all__ = ['handle_uploaded_file', 'tripcode', 'key']


def handle_uploaded_file(file, extension, post):
    """Moves uploaded file to files directory and makes thumb."""
    def make_path(dir):
        args = settings.MEDIA_ROOT, dir, post.section(), str(post.thread_id)
        return os.path.join(*args)
    directory = make_path('section')
    if not os.path.isdir(directory):
        os.makedirs(directory)
    file_path = '{0}.{1}'.format(post.pid, extension)
    m = md5()
    for chunk in file.chunks():
        m.update(chunk)
    del chunk
    file_data = {
        'post': post,
        'name': file.name,
        'type': FileType.objects.filter(extension=extension)[0],
        'size': file.size,
        'image_height': 0,
        'image_width': 0,
        'file': DjangoFile(file),
        'hash': m.hexdigest(),
    }
    f = File(**file_data)
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
            suffix='.{0}'.format(extension)) as tmp:
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


def key(text):
    """Generates key for passwords etc."""
    return sha256(text).hexdigest()
