#!/usr/bin/env python
# encoding: utf-8
"""
views.py

Created by Paul Bagwell on 2011-03-15.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import simplejson as json
from board.shortcuts import rtr, render_to_json


def api(request):
    return rtr('api.html', request)


def settings_root(request):
    d = request.session.get('settings') or {}
    return render_to_json(dict(d))


def settings(request, key):
    """This is used to work with user settings.

       * GET method gets settings key. If settings key is empty, it returns
       None.
       * POST method sets settings key to value.
       * DELETE method resets settings key.       
    """
    try:
        s = request.session['settings']
    except KeyError:
        s = request.session['settings'] = {}
    if request.method == 'GET':
        value = s.get(key)
    elif request.method == 'POST':
        try:
            value = request.POST['data']
            if value:
                s[key] = value
            elif key in s:
                del s[key]
            request.session.modified = True
        except (KeyError, ValueError):
            return HttpResponseBadRequest('')
    elif request.method == 'DELETE':
        s[key] = None
    return render_to_json({key: value})


