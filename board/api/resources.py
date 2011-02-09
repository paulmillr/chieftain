#!/usr/bin/env python
# encoding: utf-8
"""
resources.py

Created by Paul Bagwell on 2011-02-03.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from board import tools, validators
from board.api import emitters
from board.models import *
from djangorestframework.resource import Resource
from djangorestframework.modelresource import ModelResource, RootModelResource
from djangorestframework.response import Response, status

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

class PostRootResource(RootModelResource):
    """A create/list resource for Post."""
    allowed_methods = anon_allowed_methods = ('GET', 'POST')
    form = PostForm
    fields = (
        'id', 'pid', 'poster', 'tripcode', 'topic', 'is_op_post', 
        'date', 'message', 'email', 'html', 
        ('thread', ('id', ('section', ('id', 'slug')))),
    )
    
    def post(self, request, auth, content, *args, **kwargs):
        return Response(status.CREATED, validators.post(request))

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
    def delete(self, request, auth, *args, **kwargs):
        """Deletes post."""
        id = kwargs['id']
        p = Post.objects.get(id=id)
        k = tools.key(request.GET['password'])
        if p.password != k:
            return Response(status.FORBIDDEN)
        p.remove()
        return Response(status.NO_CONTENT)

class ThreadRootResource(RootModelResource):
    """A create/list resource for Thread."""
    allowed_methods = ('GET',)
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

