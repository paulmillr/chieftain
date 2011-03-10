#!/usr/bin/env python
# encoding: utf-8
"""
settings.py

Created by Paul Bagwell on 2011-02-26.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""

from django import template
from django.conf import settings
register = template.Library()


@register.simple_tag
def setting(name):
    return unicode(settings.__getattr__(name))
