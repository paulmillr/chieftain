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
from django.utils.translation import ugettext as _
from djangorestframework.resource import Resource
from djangorestframework.modelresource import ModelResource, RootModelResource
from djangorestframework.response import Response, status

__all__ = [
    'Resource', 'ModelResource', 'RootModelResource', 'post_validator',
    'PostRootResource', 'PostResource',
    'ThreadRootResource', 'ThreadResource',
    'SectionRootResource', 'SectionResource',
    'FileTypeRootResource', 'FileTypeResource',
    'FileGroupRootResource', 'FileGroupResource',
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


class RootModelResource(RootModelResource, Resource):
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
        try:
            instance = validators.post(request, auth)
        except validators.ValidationError as e:
            return Response(status.BAD_REQUEST, {'detail': e})
        return Response(status.CREATED, instance)


class PostResource(ModelResource):
    """A read/delete resource for Post."""
    allowed_methods = anon_allowed_methods = ('GET', 'DELETE')
    model = Post
    fields = (
        'id', 'pid', 'poster', 'tripcode', 'topic', 'is_op_post',
        'date', 'message', 'email', 'html',
        ('thread', ('id', ('section', ('id', 'slug')))),
    )
    
    #def get(self, request, auth, *args, **kwargs):
    #    self.model.thread

    def delete(self, request, auth, *args, **kwargs):
        """Deletes post."""
        post = Post.objects.get(id=kwargs['id'])
        key = request.GET['password']
        if len(key) < 64:  # make hash if we got plain text password
            key = tools.key(key)

        if post.password != key:
            detail = u'{0}{1}. {2}'.format(
                _('Error on deleting post #'), post.pid,
                _('Password mismatch')
            )
            return Response(status.FORBIDDEN, content={'detail': detail})
        post.remove()
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


class FileTypeRootResource(RootModelResource):
    """A list resource for FileType."""
    allowed_methods = anon_allowed_methods = ('GET',)
    model = FileType
    fields = ('id', 'category_id', 'type', 'extension')


class FileTypeResource(ModelResource):
    """A read resource for FileType."""
    allowed_methods = anon_allowed_methods = ('GET',)
    model = FileType
    fields = ('id', 'category_id', 'type', 'extension')


class FileGroupRootResource(RootModelResource):
    """A list resource for FileGroup."""
    allowed_methods = anon_allowed_methods = ('GET',)
    model = FileGroup
    fields = ('id', 'name')


class FileGroupResource(ModelResource):
    """A read resource for FileGroup."""
    allowed_methods = anon_allowed_methods = ('GET',)
    model = FileGroup
    fields = ('id', 'name')
