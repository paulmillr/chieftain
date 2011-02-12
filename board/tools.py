#!/usr/bin/env python
# encoding: utf-8
"""
tools.py

Created by Paul Bagwell on 2011-01-30.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
import os
import re
import Image
from hashlib import md5, sha256
from string import maketrans
from crypt import crypt
from klipped import settings
from datetime import datetime
from board.models import File, FileType

__all__ = ['handle_uploaded_file', 'tripcode', 'key']


def handle_uploaded_file(file, extension, post):
    """Moves uploaded file to files directory and makes thumb."""
    directory = os.path.join(settings.MEDIA_ROOT, 'sections', post.section(),
        str(post.thread_id))
    file_path = '{0}.{1}'.format(post.pid, extension)
    path = os.path.join(directory, file_path)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    file_data = {
        'post': post,
        'name': file.name,
        'mime': FileType.objects.get(extension=extension),
        'size': file.size,
        'image_height': 0,
        'image_width': 0,
    }
    m = md5()
    with open(path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
            m.update(chunk)
    file_data['hash'] = m.hexdigest()
    #try:  # make thumb
    #    img = Image.open(file)
    #    THUMB_SIZE = 200, 200
    #    img.thumbnail(THUMB_SIZE)
    #    img.save(outfile)
    #    thumb_path = outfile
    #except IOError:
    #    thumb_path = filegroup.image
    file_data['file'] = destination
    print file_data
    f = File(**file_data).save()
    #return f


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
