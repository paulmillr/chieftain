#!/usr/bin/env python
# encoding: utf-8
"""
context_processors.py

Created by Paul Bagwell on 2011-02-07.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from django.conf import settings as _settings
from board.middleware import set_session_defaults


def settings(request):
    """Adds settings dict to all requests with Context."""
    #print request
    return {'settings': _settings}


def session(request):
    """Returns str of session settings keys.

       Example:
       s = request.session['settings']
       s['test'] = 551
       s['test_2'] = 120
       {'session_classes': 'test test2'}
    """
    # usually this is set by middleware, but
    # when user logs out, session destroys itself and we need to reinit it
    if 'settings' not in request.session:
        set_session_defaults(request)
    session = request.session
    settings = session['settings']
    user = request.user

    def pop_from_session(key, default=''):
        return settings.pop(key) if settings.get(key) else default

    if session.get('no_captcha'):
        settings['no_captcha'] = True

    if user.is_authenticated():
        settings['is_mod'] = True
        if user.is_superuser:
            settings['is_admin'] = True
    return {
        'style': pop_from_session('style', 'photon'),
        'password': pop_from_session('password'),
        'session': dict(settings.items()),
        'session_classes': ' '.join(settings.keys()),
        'hidden': list(session['hidden']),
        'feed': list(session['feed']),
    }
