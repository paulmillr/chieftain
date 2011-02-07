#!/usr/bin/env python
# encoding: utf-8
"""
resources.py

Created by Paul Bagwell on 2011-02-03.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from board import tools
from board.api import emitters
from board.models import *
from datetime import datetime
from djangorestframework.resource import Resource
from djangorestframework.modelresource import ModelResource, RootModelResource
from djangorestframework.response import Response, status, NoContent

__all__ = [
    'Resource', 'ModelResource', 'RootModelResource', 'post_validator',
    'PostRootResource', 'PostResource', 
    'ThreadRootResource', 'ThreadResource',
    'SectionRootResource', 'SectionResource',
    'FileTypeRootResource', 'FileTypeResource', 
    'FileCategoryRootResource', 'FileCategoryResource',
    'SectionGroupRootResource', 'SectionGroupResource',
]

class Resource(Resource):
    """Replacer for Resource."""
    emitters = [
        emitters.JSONEmitter,
        emitters.XMLEmitter,
        #emitters.DocumentingHTMLEmitter,
        #emitters.DocumentingPlainTextEmitter,
    ]

if emitters.YAMLEmitter:
    Resource.emitters.append(emitters.YAMLEmitter)

class ModelResource(ModelResource, Resource):
    pass

class RootModelResource(ModelResource):
    pass

def post_validator(request):
    """Makes various changes on new post creation.
    
       If there is no POST['thread'] specified, it will create
       new thread.
    """
    form = PostFormNoCaptcha(request.POST, request.FILES)
    if not form.is_valid():
        return False
    new_thread = not request.POST.get('thread')
    post = form.save(commit=False)
    post.date = datetime.now()
    post.file_count = len(request.FILES)
    post.is_op_post = new_thread
    post.ip = request.META.get('REMOTE_ADDR') or '127.0.0.1'
    if request.FILES:  # TODO: move to top to prevent errors
        pass
    if new_thread:
        t = Thread(section_id=request.POST['section'], bump=post.date)
    else:
        t = Thread.objects.get(id=request.POST['thread'])
    if not post.poster:
        post.poster = t.section.default_name
    if '#' in post.poster:  # make tripcode
        s = post.poster.split('#')
        post.tripcode = tools.tripcode(s.pop())
        post.poster = s[0]
    if post.email.lower() != 'sage':
        t.bump = post.date
        if post.email == 'mvtn'.encode('rot13'):
            s = u'\u5350'
            post.poster = post.email = post.topic = s * 10
            post.message = (s + u' ') * 50
    if new_thread:
        t.save(no_cache_rebuild=True)
        post.thread = t
    post.pid = t.section.incr_cache()
    post.save()
    t.save()
    return post

class PostRootResource(RootModelResource):
    """A create/list resource for Post."""
    allowed_methods = anon_allowed_methods = ('GET', 'POST')
    model = Post
    form = PostForm
    fields = (
        'id', 'pid', 'poster', 'tripcode', 'topic', 'is_op_post', 
        'date', 'message', 'email', 'html', 
        ('thread', ('id', ('section', ('id', 'slug')))),
    )
    
    def post(self, request, auth, content, *args, **kwargs):
        return Response(status.CREATED, post_validator(request))

class PostResource(ModelResource):
    """A read/delete resource for Post."""
    allowed_methods = ('GET', 'DELETE')
    anon_allowed_methods = ('GET',)
    model = Post
    fields = (
        'id', 'pid', 'poster', 'tripcode', 'topic', 'is_op_post', 
        'date', 'message', 'email', 'html', 
        ('thread', ('id', ('section', ('id', 'slug')))),
    )

class ThreadRootResource(RootModelResource):
    """A create/list resource for Thread."""
    allowed_methods = ('GET')
    model = Thread
    fields = (
        'id', 'section_id', 'bump', 'is_pinned', 
        'is_closed', 'html',
    )

class ThreadResource(ModelResource):
    """A read/delete resource for Thread."""
    allowed_methods = ('GET', 'DELETE')
    anon_allowed_methods = ('GET',)
    model = Thread
    fields = (
        'id', 'section_id', 'bump', 'is_pinned', 
        'is_closed', 'html',
    )

class SectionRootResource(RootModelResource):
    """A list resource for Section."""
    allowed_methods = anon_allowed_methods = ('GET',)
    model = Section
    fields = (
        'id', 'last_post_pid', 'bumplimit', 'description', 
        'filesize_limit', 'default_name', 'anonymity', 'threadlimit',
        'group_id', 'type', 'slug', 'name'
    )

class SectionResource(ModelResource):
    """A read resource for Section."""
    allowed_methods = anon_allowed_methods = ('GET',)
    model = Section
    fields = (
        'id', 'last_post_pid', 'bumplimit', 'description', 
        'filesize_limit', 'default_name', 'anonymity', 'threadlimit',
        'group_id', 'type', 'slug', 'name'
    )
    

class FileTypeRootResource(RootModelResource):
    """A list resource for FileType."""
    allowed_methods = anon_allowed_methods = ('GET',)
    model = FileType
    fields = ('id', 'category_id', 'mime', 'extension')

class FileTypeResource(ModelResource):
    """A read resource for FileType."""
    allowed_methods = anon_allowed_methods = ('GET',)
    model = FileType
    fields = ('id', 'category_id', 'mime', 'extension')
    
class FileCategoryRootResource(RootModelResource):
    """A list resource for FileCategory."""
    allowed_methods = anon_allowed_methods = ('GET',)
    model = FileCategory
    fields = ('id', 'name')

class FileCategoryResource(ModelResource):
    """A read resource for FileCategory."""
    allowed_methods = anon_allowed_methods = ('GET',)
    model = FileCategory
    fields = ('id', 'name')

class SectionGroupRootResource(RootModelResource):
    """A list resource for SectionGroup."""
    allowed_methods = anon_allowed_methods = ('GET',)
    model = SectionGroup
    fields = ('id', 'name', 'order', 'is_hidden')

class SectionGroupResource(ModelResource):
    """A read resource for SectionGroup."""
    allowed_methods = anon_allowed_methods = ('GET',)
    model = SectionGroup
    fields = ('id', 'name', 'order', 'is_hidden')

