#!/usr/bin/env python
# encoding: utf-8
"""
resources.py

Created by Paul Bagwell on 2011-02-03.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from datetime import datetime
from django.utils.translation import ugettext as _
from djangorestframework.resource import Resource
from djangorestframework.modelresource import ModelResource, RootModelResource
from djangorestframework.response import Response, status, ResponseException
from board import tools, validators, template
from api import emitters
from board.models import *
from modpanel.views import is_mod

__all__ = [
    'Resource', 'ModelResource', 'RootModelResource',
    'PostStreamResource',
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
            kwargs['pid'] = kwargs.pop('id')
            kwargs['thread__section__slug'] = kwargs.pop('section__slug')
            op_post = Post.objects.get(**kwargs)
            inst = op_post.thread
        except (Post.DoesNotExist, self.model.DoesNotExist):
            raise ResponseException(status.NOT_FOUND)
        res = {}
        for f in self.fields:
            res[f] = inst.__getattribute__(f)
        pf = [f for f in list(PostResource.fields)
            if isinstance(f, str) and f != 'files']
        res['posts'] = inst.post_set.filter(is_deleted=False).values(*pf)
        return res


class PostStreamResource(RootModelResource):
    """docstring for PostStreamResource"""
    allowed_methods = anon_allowed_methods = ('GET', 'POST')
    model = Post

    def get(self, request, auth, *args, **kwargs):
        try:
            ts = tools.from_timestamp(request.GET['timestamp'])
            new_posts = Post.objects.filter(
                date__gt=ts,
                thread=kwargs['thread'],
                is_deleted=False,
            )
            posts = []
            if new_posts.count():
                posts = new_posts.values('html', 'pid')
        except KeyError:
            return Response(status.BAD_REQUEST, {'detail': 'TS'})
        return Response(status.OK, {'posts': posts})


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
        # django sends date with microseconds. We don't want it.
        instance.date = instance.date.strftime('%Y-%m-%d %H:%M:%S')
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
        if len(key) < 40:  # make hash if we got plain text password
            key = tools.key(key)

        if post.password == key:
            post.remove()
            return Response(status.NO_CONTENT)
        elif is_mod(request, post.section_slug()):
            if request.GET.get('ban_ip'):
                r = request.GET.get('ban_reason')
                if not r:
                    return Response(status.BAD_REQUEST, {
                    'detail': _('You need to enter ban reason')})
                d = DeniedIP(ip=post.ip, reason=r, by=request.user)
                d.save()
            if request.GET.get('delete_all'):
                slug = post.section_slug()
                posts = post.section().posts(
                    ).filter(ip=post.ip, is_deleted=False)
                # remove threads
                print posts
                op = posts.filter(is_op_post=True).values('pid', 'thread')
                template.rebuild_cache(slug, [i['pid'] for i in op])
                t = Thread.objects.filter(id__in=[i['thread'] for i in op])
                t.update(is_deleted=True)
                #posts.update(is_deleted=True)
                for p in posts:
                    p.remove()
            else:
                post.remove()
            post.thread.rebuild_template_cache()
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
        if len(key) < 40:  # make hash if we got plain text password
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
