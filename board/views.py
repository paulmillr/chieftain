#!/usr/bin/env python
# encoding: utf-8
"""
views.py

Created by Paul Bagwell on 2011-01-13.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from django.core.paginator import Paginator
from django.http import (Http404, HttpResponseRedirect,
    HttpResponsePermanentRedirect)
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from board import validators
from board.models import *
from board.shortcuts import *
from board.tools import make_post_description
from modpanel.views import is_mod

__all__ = [
    'index', 'settings', 'faq', 'search',
    'section', 'threads', 'posts', 'thread',
]


def index(request):
    bposts = Post.objects.filter(is_op_post=True, id__in=request.session.get(
        'bookmarks', []))

    #Thread.objects.filter
    return render(request, 'index.html', add_sidebar({
        'popular': Post.objects.popular(10),
        'bookmarks': (make_post_description(p) for p in bposts),
        'random_images': File.objects.random_images()[:3],
    }))


def settings(request):
    return render(request, 'settings.html', add_sidebar())


def faq(request):
    return render(request, 'faq.html', add_sidebar())


def search(request, section_slug, page):
    section = get_object_or_404(Section, slug=section_slug)
    is_op_post = request.GET.get('is_op_post') or False
    posts = Post.objects.filter(is_op_post=is_op_post,
        thread__section=section,
        message__contains=request.GET['q']).order_by('-date')
    if not posts.count():
        return render(request, 'client_error.html', add_sidebar({
            'details': _('Nothing found')
        }))
    p = get_page_or_404(Paginator(posts, section.ONPAGE), page)
    return render(request, 'section_posts.html', add_sidebar({'posts': p,
        'section': section}))


def post_router(request, op_post=None):
    """Routes post creation requests."""
    try:
        p = validators.post(request, no_captcha=False)
    except validators.ValidationError as e:
        return render(request, 'error.html', {'details': e})
    if not p:  # display error page
        return render(request, 'error.html', add_sidebar({
            'errors': PostForm(p).errors
        }))
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
    return render(request, 'section_page.html', add_sidebar({
        'threads': t,
        'section': s,
        'form': PostForm()
    }))


def threads(request, section_slug):
    """List of OP-posts in section."""
    section = get_object_or_404(Section, slug=section_slug)
    return render(request, 'section_threads.html', add_sidebar({
        'threads': section.op_posts(),
        'section': section,
        'form': PostForm(),
        'mod': is_mod(request, section_slug)
    }))


def posts(request, section_slug, page):
    """List of posts in section."""
    section = get_object_or_404(Section, slug=section_slug)
    p = get_page_or_404(Paginator(section.posts(), section.ONPAGE), page)
    return render(request, 'section_posts.html', add_sidebar({
        'posts': p,
        'section': section,
        'form': PostForm(),
        'mod': is_mod(request, section_slug)
    }))


def images(request, section_slug, page):
    """List of images in section."""
    # TODO
    section = get_object_or_404(Section, slug=section_slug)
    images_page = Paginator(section.images(), 100)


def thread(request, section_slug, op_post):
    """Thread and its posts."""
    if request.method == 'POST':
        return post_router(request, op_post)
    post = get_object_or_404(Post, thread__section__slug=section_slug,
        pid=op_post)
    thread = post.thread
    if thread.poll_id:
        ip = request.META['REMOTE_ADDR']
        thread.poll.vote_data = thread.poll.get_vote_data(ip)
    if thread.is_deleted:
        raise Http404
    if not post.is_op_post:
        return HttpResponsePermanentRedirect('/{0}/{1}#post{2}'.format(
            thread.section, thread.op_post.pid, post.pid))
    return render(request, 'section_thread.html', add_sidebar({
        'thread': thread,
        'form': PostForm(),
        'mod': is_mod(request, section_slug),
    }))
