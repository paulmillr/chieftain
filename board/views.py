#!/usr/bin/env python
# encoding: utf-8
"""
views.py

Created by Paul Bagwell on 2011-01-13.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from board.models import Post, File, Section, PostForm
from board.shortcuts import get_page_or_404, add_sidebar
from board.tools import make_post_descriptions

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
        'bookmarks': make_post_descriptions(bposts),
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
        message__contains=request.GET['q']
    ).order_by('-date')
    if not posts.count():
        return render(request, 'client_error.html', add_sidebar({
            'details': _('Nothing found')
        }))
    p = get_page_or_404(Paginator(posts, section.ONPAGE), page)
    return render(request, 'search_results.html', add_sidebar({'posts': p,
        'section': section}))


def storage(request):
    section = request.GET.get('section')
    if section:
        session_posts = request.session.get(section, {})
        posts = Post.objects.filter(id__in=session_posts)
        return render(request, 'storage_tab.html', {
            'posts': make_post_descriptions(posts)
        })
    return render(request, 'storage.html', add_sidebar())


def section(request, section_slug, page):
    """
    Gets 20 threads from current section with
    OP post and last 5 posts in each thread.
    """
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
        'form': PostForm()
    }))


def images(request, section_slug, page):
    """TODO: List of images in section."""
    section = get_object_or_404(Section, slug=section_slug)
    images_page = Paginator(section.images(), 100)
    return render(request, 'section_images.html', add_sidebar({
        'images_page': images_page,
        'section': section,
    }))


def thread(request, section_slug, op_post):
    """Thread and its posts."""
    post = get_object_or_404(Post, thread__section__slug=section_slug,
        pid=op_post, is_deleted=False)
    thread = post.thread
    if thread.poll_id:
        ip = request.META['REMOTE_ADDR']
        thread.poll.vote_data = thread.poll.get_vote_data(ip)
    if not post.is_op_post:
        return redirect('/{0}/{1}#post{2}'.format(
            thread.section, thread.op_post.pid, post.pid))
    return render(request, 'section_thread.html', add_sidebar({
        'thread': thread,
        'form': PostForm(),
    }))
