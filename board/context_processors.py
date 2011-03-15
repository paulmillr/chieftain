#!/usr/bin/env python
# encoding: utf-8
"""
context_processors.py

Created by Paul Bagwell on 2011-02-07.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""

from django.conf import settings as _settings


def settings(request):
    """Adds settings dict to all requests with Context."""
    return {'settings': _settings}
