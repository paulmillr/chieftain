#!/usr/bin/env python
# encoding: utf-8
"""
shortcuts.py

Created by Paul Bagwell on 2011-02-22.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""

import codecs
from django.core.paginator import InvalidPage, EmptyPage
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson as json

__all__ = [
    'get_page_or_404', 'update_context', 'render_to_json',
    'render_to_file', 'rtr'
]


def get_page_or_404(paginator, page):
    """Gets page from Paginator instance or raises Http404 error."""
    try:
        return paginator.page(page)
    except (InvalidPage, EmptyPage):
        raise Http404


def update_context(context):
    """Updates context dictionary with sidebar."""
    from board.models import SectionGroup  # block recursive import
    context.update({'navigation': SectionGroup.objects.sections()})
    return context


def render_to_json(data):
    return HttpResponse(json.dumps(data))


def render_to_file(template, filename, request, context):
    """Renders template to filename."""
    with codecs.open(filename, 'w', 'utf-8') as f:
        f.write(render_to_string(template, context, RequestContext(request)))


def rtr(template, request, context={}, no_update=False):
    """Wrapper around render_to_response.

       Adds sidebar to all requests.
    """
    if not no_update:
        context = update_context(context)
    return render_to_response(template, context,
        context_instance=RequestContext(request))
