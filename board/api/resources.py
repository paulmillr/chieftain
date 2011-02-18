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
from djangorestframework.response import Response, status, ResponseException

__all__ = [
    'Resource', 'ModelResource', 'RootModelResource', 'post_validator',
    'PostRootResource', 'PostResource',
    'ThreadRootResource', 'ThreadResource',
    'SectionRootResource', 'SectionResource',
    'FileRootResource', 'FileResource',
    'FileTypeRootResource', 'FileTypeResource',
    'FileTypeGroupRootResource', 'FileTypeGroupResource',
    'SectionGroupRootResource', 'SectionGroupResource',
]


class Resource(Resource):
    """Replacer for Resource."""
    emitters = [
        emitters.JSONEmitter,
        emitters.XMLEmitter,
        emitters.DocumentingHTMLEmitter,
        emitters.JSONTextEmitter,
        #emitters.DocumentingPlainTextEmitter,
    ]

if emitters.YAMLEmitter:
    Resource.emitters.append(emitters.YAMLEmitter)


class ModelResource(ModelResource, Resource):
    pass


class RootModelResource(RootModelResource, Resource):
    pass


class ThreadRootResource(RootModelResource):
    """A create/list resource for Thread."""
    allowed_methods = anon_allowed_methods = ('GET',)
    model = Thread
    fields = (
        'id', 'section_id', 'bump', 'is_pinned',
        'is_closed', 'html',
    )

    def get(self, request, auth, *args, **kwargs):
        return self.model.objects.filter(is_deleted=False)[:20]


class ThreadResource(ModelResource):
    """A read/delete resource for Thread."""
    allowed_methods = ('GET', 'DELETE')
    anon_allowed_methods = ('GET',)
    model = Thread
    fields = (
        'id', 'section_id', 'bump', 'is_pinned',
        'is_closed', 'html',
    )

    def get(self, request, auth, *args, **kwargs):
        try:
            kwargs['is_deleted'] = False
            inst = self.model.objects.get(**kwargs)
        except self.model.DoesNotExist:
            raise ResponseException(status.NOT_FOUND)
        res = {}
        for f in self.fields:
            res[f] = inst.__getattribute__(f)
        pf = [f for f in list(PostResource.fields) if isinstance(f, str)]
        res['posts'] = inst.post_set.filter(is_deleted=False).values(*pf)
        return res


class PostRootResource(RootModelResource):
    """A create/list resource for Post."""
    allowed_methods = anon_allowed_methods = ('GET', 'POST')
    form = PostForm
    model = Post
    fields = (
        'id', 'pid', 'poster', 'tripcode', 'topic', 'is_op_post',
        'date', 'message', 'email', 'html',
        ('thread', ('id', ('section', ('id', 'slug')))),
    )

    def get(self, request, auth, *args, **kwargs):
        return self.model.objects.filter(is_deleted=False)[:20]

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
        'files',
    )

    @staticmethod
    def is_deleted_by_mod(request, post):
        user = request.user
        if user.is_authenticated():
            if user.is_superuser:
                return True
            mod = user.userprofile_set.all()
            if mod and post.section() in mod.get().modded():
                return True
        return False

    def get(self, request, auth, *args, **kwargs):
        try:
            kwargs['is_deleted'] = False
            return self.model.objects.get(**kwargs)
        except self.model.DoesNotExist:
            raise ResponseException(status.NOT_FOUND)

    def delete(self, request, auth, *args, **kwargs):
        """Deletes post."""
        try:
            post = self.model.objects.get(id=kwargs['id'])
        except self.model.DoesNotExist:
            raise ResponseException(status.NOT_FOUND)
        key = request.GET['password']
        if len(key) < 64:  # make hash if we got plain text password
            key = tools.key(key)

        if self.is_deleted_by_mod(request, post) or post.password == key:
            post.remove()
            return Response(status.NO_CONTENT)
        else:
            return Response(status.FORBIDDEN, content={
                'detail': u'{0}{1}. {2}'.format(
                    _('Error on deleting post #'), post.pid,
                    _('Password mismatch')
                )
            })


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


class FileRootResource(RootModelResource):
    """A list resource for File."""
    allowed_methods = anon_allowed_methods = ('GET',)
    model = File
    fields = ('id', 'post', 'name', 'type', 'size', 'is_deleted',
        'image_width', 'image_height', 'hash', 'file', 'thumb')


class FileResource(ModelResource):
    """A list resource for File."""
    allowed_methods = anon_allowed_methods = ('GET', 'DELETE')
    model = File
    fields = ('id', 'post', 'name', 'type', 'size', 'is_deleted',
        'image_width', 'image_height', 'hash', 'file', 'thumb')

    def delete(self, request, auth, *args, **kwargs):
        """Deletes attachment."""
        try:
            file = self.model.objects.get(**kwargs)
        except self.model.DoesNotExist:
            raise ResponseException(status.NOT_FOUND)

        key = request.GET['password']
        if len(key) < 64:  # make hash if we got plain text password
            key = tools.key(key)

        if file.post.password != key:
            raise ResponseException(status.FORBIDDEN, content={
                'detail': u'{0}{1}. {2}'.format(
                    _('Error on deleting file #'), post.pid,
                    _('Password mismatch')
                )
            })
        file.remove()
        return Response(status.NO_CONTENT)


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


class FileTypeGroupRootResource(RootModelResource):
    """A list resource for FileTypeGroup."""
    allowed_methods = anon_allowed_methods = ('GET',)
    model = FileTypeGroup
    fields = ('id', 'name')


class FileTypeGroupResource(ModelResource):
    """A read resource for FileTypeGroup."""
    allowed_methods = anon_allowed_methods = ('GET',)
    model = FileTypeGroup
    fields = ('id', 'name')
