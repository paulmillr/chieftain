#!/usr/bin/env python
# encoding: utf-8
"""
views.py

Created by Paul Bagwell on 2011-01-13.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
import sys
import re
from string import maketrans
from crypt import crypt
from datetime import datetime
from django.conf import settings as site_settings
from django.contrib.syndication.views import Feed
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import Http404, HttpResponseRedirect,\
    HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_page
from board import validators
from board.models import *

__all__ = [
    'rtr', 'index', 'settings', 'faq', 'section', 'threads', 'posts',
    'thread',
]


def rtr(template, request, dictionary={}):
    """Wrapper around render_to_response.

       Adds sidebar to all requests.
    """
    dictionary.update({'navigation': SectionGroup.objects.sections()})
    return render_to_response(template, dictionary,
        context_instance=RequestContext(request))


#@cache_page(DAY)
def index(request):
    """Main imageboard page"""
    return rtr('index.html', request)


#@cache_page(DAY)
def settings(request):
    """User settings page."""
    return rtr('settings.html', request)


def search(request):
    """Searches on the board."""
    pass


#@cache_page(DAY / 2)
def faq(request):
    """Gets FAQ page."""
    return rtr('faq.html', request)


def post_router(request, op_post=None):
    """Routes post creation requests."""
    try:
        p = validators.post(request, no_captcha=False)
    except validators.ValidationError as e:
        return rtr('error.html', request, {'details': e})
    if not p:  # display error page
        return rtr('error.html', request, {'errors': PostForm(p).errors})
    # get op post and created post pids
    args = [op_post, p.pid] if op_post else [p.pid, p.pid]
    return HttpResponseRedirect('{0}#post{1}'.format(*args))


def section(request, section_slug, page):
    """
    Gets 20 threads from current section with
    OP post and last 5 posts in each thread.
    """
    if request.method == 'POST':
        return post_router(request)
    try:
        s = Section.objects.get(slug=section_slug)
        t = s.page_threads(page)
    except (Section.DoesNotExist, InvalidPage, EmptyPage):
        raise Http404
    return rtr('section_page.html', request, {'threads': t, 'section': s,
        'form': PostForm()})

def threads(request, section_slug):
    """Gets list of OP-posts in section."""
    section = get_object_or_404(Section, slug=section_slug)
    return rtr('section_threads.html', request, {'threads': section.op_posts(), 
        'section': section, 'form': PostForm()})

def posts(request, section_slug, page):
    """Gets list of posts in section."""
    section = get_object_or_404(Section, slug=section_slug)
    posts_page = Paginator(section.posts(), section.ONPAGE)
    try:
        p = posts_page.page(page)
    except (InvalidPage, EmptyPage):
        raise Http404
    return rtr('section_posts.html', request, {'posts': p,
        'section': section, 'form': PostForm()})

def thread(request, section_slug, op_post):
    """Gets thread and its posts."""
    if request.method == 'POST':
        return post_router(request, op_post)
    try:
        post = Post.objects.by_section(section_slug, op_post)
    except Post.DoesNotExist:
        raise Http404
    thread = post.thread
    if thread.is_deleted:
        raise Http404
    if not post.is_op_post:
        return HttpResponsePermanentRedirect('/{0}/{1}#post{2}'.format(
            thread.section, thread.op_post.pid, post.pid))
    form = PostForm()
    return rtr('section_thread.html', request,
        {'thread': thread, 'form': form})
