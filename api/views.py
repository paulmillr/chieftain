#!/usr/bin/env python
# encoding: utf-8
"""
views.py

Created by Paul Bagwell on 2011-03-15.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from django.shortcuts import render
from djangorestframework import status
from djangorestframework.response import Response, ResponseException


def api(request):
    return render(request, 'api.html')


def setting_root(request):
    settings = request.session.setdefault('settings', {})
    if request.method == 'GET':
        return Response(status.OK, settings)
    elif request.method == 'POST':
        try:
            key = request.POST['key']
            value = request.POST['value']
        except KeyError:
            raise ResponseException(status.BAD_REQUEST)
        settings[key] = value
        request.session.modified = True
        return Response(status.CREATED, settings)
    elif request.method == 'DELETE':
        settings = {}
        request.session.modified = True
        return Response(status.NO_CONTENT)


def setting(request, key=None):
    """This is used to work with user settings.

       * GET method gets settings key. If settings key is empty, it returns
       None.
       * POST method sets settings key to value.
       * DELETE method resets settings key.
    """
    settings = request.session.setdefault('settings', {})
    if request.method == 'GET':
        value = settings.get(key)
    elif request.method == 'DELETE':
        value = settings[key] = None
    return Response(status.OK, {key: value})


def bookmark(request, key):
    b = request.session.setdefault('bookmarks')
    if not key:
        return Response(status.OK, s)
    

def hidden(request, key):