#!/usr/bin/env python
# encoding: utf-8
"""
views.py

Created by Paul Bagwell on 2011-01-13.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from django.core.paginator import Paginator
from django.http import Http404, HttpResponseRedirect,\
    HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from django.utils.translation import ugettext_lazy as _
from board import validators, template
from board.models import *
from board.shortcuts import *
from modpanel.views import is_mod

__all__ = [
    'index', 'settings', 'faq', 'search',
    'section', 'threads', 'posts', 'thread',
]


def index(request):
    return rtr('index.html', request)


def settings(request):
    return rtr('settings.html', request)


def faq(request):
    return rtr('faq.html', request)


def api(request):
    return rtr('api.html', request)


def search(request, section_slug, page):
    section = get_object_or_404(Section, slug=section_slug)
    is_op_post = request.GET.get('is_op_post') or False
    posts = Post.objects.filter(is_op_post=is_op_post,
        thread__section=section,
        message__contains=request.GET['q']).order_by('-date')
    if not posts.count():
        return rtr('error.html', request, {'details': _('Nothing found')})
    p = get_page_or_404(Paginator(posts, section.ONPAGE), page)
    return rtr('section_posts.html', request, {'posts': p,
            'section': section})


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
    s = get_object_or_404(Section, slug=section_slug)
    t = get_page_or_404(Paginator(s.threads(), s.ONPAGE), page)
    return template.handle_file_cache(
        'section_page.html',
        '{0}/page/{1}.html'.format(section_slug, page),
        request,
        update_context({'threads': t, 'section': s, 'form': PostForm()}),
    )


def threads(request, section_slug):
    """List of OP-posts in section."""
    section = get_object_or_404(Section, slug=section_slug)
    return template.handle_file_cache(
        'section_threads.html',
        '{0}/threads.html'.format(section_slug),
        request,
        update_context({
            'threads': section.op_posts(),
            'section': section,
            'form': PostForm(),
            'mod': is_mod(request, section_slug)
        })
    )


def posts(request, section_slug, page):
    """List of posts in section."""
    section = get_object_or_404(Section, slug=section_slug)
    p = get_page_or_404(Paginator(section.posts(), section.ONPAGE), page)
    return template.handle_file_cache(
        'section_posts.html',
        '{0}/posts/{1}.html'.format(section_slug, page),
        request,
        update_context({
            'posts': p, 'section': section, 'form': PostForm(),
            'mod': is_mod(request, section_slug)
        })
    )


def images(request, section_slug, page):
    """List of images in section."""
    section = get_object_or_404(Section, slug=section_slug)
    images_page = Paginator(section.images(), 100)


def thread(request, section_slug, op_post):
    """Thread and its posts."""
    if request.method == 'POST':
        return post_router(request, op_post)
    post = get_object_or_404(Post, thread__section__slug=section_slug,
        pid=op_post)
    thread = post.thread
    if thread.is_deleted:
        raise Http404
    if not post.is_op_post:
        return HttpResponsePermanentRedirect('/{0}/{1}#post{2}'.format(
            thread.section, thread.op_post.pid, post.pid))
    mod = is_mod(request, section_slug)
    return template.handle_file_cache(
        'section_thread.html',
        '{0}/thread/{1}.html'.format(section_slug, op_post),
        request,
        update_context({'thread': thread, 'form': PostForm(),
        'mod': is_mod(request, section_slug)})
    )
