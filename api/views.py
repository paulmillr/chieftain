#!/usr/bin/env python
# encoding: utf-8
"""
views.py

Created by Paul Bagwell on 2011-03-15.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from django.shortcuts import render
from djangorestframework import status
from djangorestframework.resource import Resource
from djangorestframework.response import Response, ResponseException


def api(request):
    return render(request, 'api.html')
