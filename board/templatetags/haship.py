#!/usr/bin/env python
# encoding: utf-8
"""
haship.py

Created by Paul Bagwell on 2011-02-21.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""

from django import template
from django.utils.safestring import mark_safe
from hashlib import md5

register = template.Library()

md = lambda x: md5(x).hexdigest()[:5]

def haship(value, arg=''):
    ip = value.split('.')
    i = [md(str(ip[:2]))]
    i.extend(ip[2:])
    return mark_safe('.'.join(i))

register.filter(haship)
