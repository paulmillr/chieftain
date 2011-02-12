#!/usr/bin/env python
# encoding: utf-8
"""
tools.py

Created by Paul Bagwell on 2011-01-30.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
import re
import Image
from hashlib import sha256
from string import maketrans
from crypt import crypt
from klipped import settings
from datetime import datetime

__all__ = ['handle_uploaded_file', 'tripcode', 'key']


def handle_uploaded_file(file, extension, post):
    """Moves uploaded file to files directory and makes thumb."""
    path = '{media_root}/{section}/{pid}.{extension}'.format(
        media_root=settings.MEDIA_ROOT, section=section.slug,
        pid=pid, extension=extension
    )
    with open(tpl, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    try:  # make thumb
        img = Image.open(file)
        THUMB_SIZE = 200, 200
        img.thumbnail(THUMB_SIZE)
        img.save(outfile)
        thumb_path = outfile
    except IOError:
        thumb_path = filegroup.image
    return path, thumb_path


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
