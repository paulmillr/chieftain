#!/usr/bin/env python
# encoding: utf-8
"""
tools.py

Created by Paul Bagwell on 2011-01-30.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
import re
from hashlib import sha256
from string import maketrans
from crypt import crypt

__all__ = ['handle_uploaded_file', 'tripcode', 'key']


def handle_uploaded_file(f, section, thread, post):
    """Moves uploaded file to files directory and makes thumb."""
    tpl = '{media_root}{section}/{thread}/{post}'.format(
        media_root=MEDIA_ROOT, section=section, thread=thread, post=post
    )
    destination = open(tpl, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()


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