t#!/usr/bin/env python
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


def storage(request, storage_name, is_dict=False, key=''):
    """Used to work with user settings.

    * storage_name - name of key in request.session
    * is_dict - type of value, dict or set
    * key - name of key in our storage. Though:
    storage(..., key='settings') -> request.session[storage_name][key]
    If is_dict is disabled, key would specify value of element in the set.
    """
    default = {} if is_dict else set()
    data = request.session.setdefault(storage_name, default)
    if request.method == 'GET':  # get all data
        if is_dict and key:
            data = data.get(key)
        return Response(status.OK, data)
    elif request.method == 'POST':
        try:
            key = request.POST['key']
            if is_dict:
                value = request.POST['value']
        except KeyError:
            raise ResponseException(status.BAD_REQUEST)
        if is_dict:
            data[key] = value
        else:
            data.add(key)
        request.session.modified = True
        return Response(status.CREATED, data)
    elif request.method == 'PUT' and is_dict and key:  # alias for POST w/key
        try:
            value = request.POST['value']
        except KeyError:
            raise ResponseException(status.BAD_REQUEST)
        data[key] = value
        return Response(status.CREATED, data)
    elif request.method == 'DELETE':
        if not key:  # clear whole storage
            data = set()
        else:
            if is_dict:
                data[key] = None
            else:
                data.remove(key)
        request.session.modified = True
        return Response(status.NO_CONTENT)
