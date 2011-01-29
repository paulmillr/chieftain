#!/usr/bin/env python
# encoding: utf-8
"""
views.py

Created by Paul Bagwell on 2011-01-13.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
import sys
from datetime import datetime
from django.core.paginator import InvalidPage, EmptyPage
from django.http import Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.cache import cache_page
from board.models import *

__all__ = [
    'rtr', 'check_form', 'index', 'settings', 'faq', 'section', 'thread',
]


def rtr(template, request, dictionary={}):  # wrapper around render_to_response
    dictionary.update({'navigation': SectionGroup.objects.sections()})
    return render_to_response(template, dictionary,
        context_instance=RequestContext(request))


def handle_uploaded_file(f, section, thread, post):
    tpl = '{media_root}{section}/{thread}/{post}'.format(
        media_root=MEDIA_ROOT, section=section, thread=thread, post=post
    )
    destination = open(tpl, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()


def check_form(request, new_thread=False):
    """Makes various changes on new post creation."""
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
        model = form.save(commit=False)
        if 'REMOTE_ADDR' in request.META:
            model.ip = request.META['REMOTE_ADDR']
        model.date = datetime.now()
        model.file_count = len(request.FILES)
        model.is_op_post = new_thread
        if new_thread:
            t = Thread(section_id=request.POST['section'], bump=model.date)
        else:
            t = Thread.objects.get(id=request.POST['thread'])
        model.pid = t.section.incr_cache()
        if not model.poster:
            model.poster = t.section.default_name
        if model.email.lower() != 'sage':
            t.bump = model.date
            if model.email == 'mvtn'.encode('rot13'):
                s = u'\u5350'
                model.poster = model.email = model.topic = s * 10
                model.message = (s + u' ') * 50
        if new_thread:
            t.save(no_cache_rebuild=True)
            model.thread = t
        if request.FILES:
            pass
            #handle_uploaded_file(request.FILES['file'], t.section, t, model.pid)
            #f = File(post=model, mime='image/jpeg')
        model.save()
        t.save()
        op_post = model.pid if new_thread else t.op_post.pid
        return HttpResponseRedirect('{0}#post{1}'.format(op_post, model.pid))
    else:
        return rtr('error.html', request, {'errors': form.errors})

#@cache_page(DAY)
def index(request):
    """Main imageboard page"""
    return rtr('index.html', request)


#@cache_page(DAY)
def settings(request):
    """User settings page"""
    return rtr('settings.html', request)


#@cache_page(DAY / 2)
def faq(request):
    return rtr('faq.html', request)


def section(request, section, page=1):
    """
    Gets 20 threads from current section with
    OP post and last 5 posts in each thread
    """
    if request.method == 'POST':
        return check_form(request, True)
    try:
        s = Section.objects.get(slug__exact=section)
        t = s.page_threads(page)
    except (Section.DoesNotExist, InvalidPage, EmptyPage):
        raise Http404
    form = PostForm()
    return rtr('section.html', request, {'threads': t, 'section': s,
        'form': form})


def thread(request, section, op_post):
    """Gets thread and its posts"""
    if request.method == 'POST':
        return check_form(request, False)
    try:
        post = Post.objects.by_section(section, op_post)
    except Post.DoesNotExist:
        raise Http404
    thread = post.thread
    if thread.op_post.id != post.id:
        return HttpResponsePermanentRedirect('/{0}/{1}#post{2}'.format(\
            thread.section, thread.op_post.pid, post.pid))
    form = PostForm()
    return rtr('thread.html', request, {'thread': thread, 'form': form})
