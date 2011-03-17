#!/usr/bin/env python
# encoding: utf-8
"""
template.py

Created by Paul Bagwell on 2011-02-22.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""

import os
import shutil
from django.conf import settings
from django.http import HttpResponse
from board.shortcuts import rtr, render_to_file

__all__ = ['handle_file_cache', 'rebuild_cache']



def handle_file_cache(template, filename, request, context):
    return rtr(template, request, context, True)


def rebuild_cache(section_slug=None, item=None):
    pass
