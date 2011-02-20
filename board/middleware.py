#!/usr/bin/env python
# encoding: utf-8
"""
middleware.py

Created by Paul Bagwell on 2011-01-30.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from django.template import RequestContext
from django.template.loader import render_to_string
from django.http import HttpResponseForbidden
from board.models import DeniedIP, AllowedIP

__all__ = ['DenyMiddleware', 'AllowMiddleware']


METHODS = ('GET', 'POST', 'UPDATE', 'DELETE')
WHITELIST = ()


def ip_in(ip, model):
    """
    Returns True if the given ip address is in one of the ban models
    """
    try:
        for i in model.objects.all():
            if ip in i.network():
                return i.reason if i.reason else ''
    except ValueError:
        pass
    return False


def get_ip(request):
    """Gets the true client IP address of the request.

       Contains proxy handling involving HTTP_X_FORWARDED_FOR
       and multiple addresses.
    """
    ip = request.META['REMOTE_ADDR']
    if not ip or ip == '127.0.0.1' and 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    try:  # choose first of (possibly) multiple values
        return ip.replace(',', '').split()[0]
    except IndexError:
        return request.META['REMOTE_ADDR']


def forbid(request, reason=''):
    """
    Forbids a user to access the site
    Cleans up their session (if it exists)
    Returns a templated HttpResponseForbidden when banning requests
    Override the `403.html` template to customize the error report
    """
    for k in request.session.keys():
        del request.session[k]
    return HttpResponseForbidden(render_to_string('banned.html',
        {'reason': reason}, context_instance=RequestContext(request)))


class DenyMiddleware(object):
    """
    Forbids any request if they are in the DeniedIP list
    """
    def process_request(self, request):
        ip = get_ip(request)
        if not request.method in METHODS or ip in WHITELIST:
            return False
        reason = ip_in(ip, DeniedIP)
        # not simply 'if reason:' because it could return empty string
        if reason is not False:
            return forbid(request, reason)


class AllowMiddleware(object):
    """
    Forbids any request if they are not in the AllowedIP list
    """
    def process_request(self, request):
        if not request.method in METHODS:
            return False
        if not ip_in(get_ip(request), AllowedIP):
            return forbid(request)
