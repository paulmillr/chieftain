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


class Resource(Resource):
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

class RootModelResource(RootModelResource, Resource):
    pass
        

def check_form(request, new_thread=False):
    """Makes various changes on new post creation."""
    form = PostForm(request.POST, request.FILES)
    if not form.is_valid():
        return False
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
    if model.poster:
        if '#' in model.poster:
            s = model.poster.split('#')
            model.tripcode = tools.tripcode(s.pop())
            model.poster = s[0]
    else:
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
    model.save()
    t.save()
    #op_post = model.pid if new_thread else t.op_post.pid
    return model

class PostRootResource(RootModelResource):
    """A create/list resource for Post."""
    allowed_methods = anon_allowed_methods = ('GET', 'POST')
    model = Post
    fields = (
        'id', 'pid', 'poster', 'tripcode', 'topic', 'is_op_post', 
        'date', 'message', 'email', 'html', 
        ('thread', ('id', ('section', ('id', 'slug')))),
    )

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
    allowed_methods = ('GET', 'POST')
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

