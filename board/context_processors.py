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


def session(request):
    """Returns str of session settings keys.

       Example:
       s = request.session['settings']
       s['test'] = 551
       s['test_2'] = 120
       {'session_classes': 'test test2'}
    """
    s = request.session.get('settings', {})
    def pop_from_session(key, default=''):
        return s.pop(key) if s.get(key) else default
    u = request.user
    if u.is_authenticated():
        s['is_mod'] = True
        if u.is_superuser:
            s['is_admin'] = True
    return {
        'style': pop_from_session('style', 'photon'),
        'password': pop_from_session('password'),
        'session': dict(s.items()),
        'session_classes': ' '.join(s.keys()),
    }
