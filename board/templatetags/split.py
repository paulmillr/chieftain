#!/usr/bin/env python
# encoding: utf-8
"""
haship.py

Created by Paul Bagwell on 2011-04-23.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from django import template
register = template.Library()


@register.filter
def split(str, splitter):
    return str.split(splitter)
