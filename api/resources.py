#!/usr/bin/env python
# encoding: utf-8
"""
resources.py

Created by Paul Bagwell on 2011-02-03.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
import urllib
import urllib2
from django.utils.translation import ugettext as _
from djangorestframework import status
from djangorestframework.resource import Resource
from djangorestframework.modelresource import ModelResource, RootModelResource
from djangorestframework.response import Response, ResponseException
from board import tools, validators, template
from api import emitters
from board.models import *
from modpanel.views import is_mod

__all__ = [
    'Resource', 'ModelResource', 'RootModelResource',
    'PollRootResource', 'PollResource',
    'ChoiceRootResource', 'ChoiceResource',
    'VoteRootResource', 'VoteResource',
    'ThreadRootResource', 'ThreadResource',
    'PostRootResource', 'PostResource',
    'SectionRootResource', 'SectionResource',
    'FileRootResource', 'FileResource',
    'FileTypeRootResource', 'FileTypeResource',
    'FileTypeGroupRootResource', 'FileTypeGroupResource',
    'SectionGroupRootResource', 'SectionGroupResource',
]


class Resource(Resource):
    """Replacer for Resource."""
    allowed_methods = anon_allowed_methods = ('GET',)
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


#def admin(request, mode):

class PollRootResource(RootModelResource):
    """A list resource for Poll."""
    model = Poll


class PollResource(ModelResource):
    """A read resource for Poll."""
    model = Poll


class ChoiceRootResource(RootModelResource):
    """A list resource for Choice."""
    model = Choice


class ChoiceResource(ModelResource):
    """A read resource for Choice."""
    model = Choice


class VoteRootResource(RootModelResource):
    """A list/create resource for Vote."""
    allowed_methods = anon_allowed_methods = ('GET', 'POST')
    model = Vote

    def post(self, request, auth, *args, **kwargs):
        try:
            choice = Choice.objects.get(id=request.POST['choice'])
        except Choice.DoesNotExist:
            raise ResponseException(status.NOT_FOUND)
        ip = request.META['REMOTE_ADDR']
        check = Vote.objects.filter(ip=ip, poll=choice.poll)
        if check:
            vote = check.get()
            vote.choice.vote_count -= 1
            vote.choice.save()
            vote.choice = choice
            vote.poll = choice.poll
        else:
            vote = Vote(poll=choice.poll, choice=choice, ip=ip)
        vote.save()
        choice.vote_count += 1
        choice.save()
        return Response(status.CREATED, choice.poll.choices().values())


class VoteResource(ModelResource):
    """A read resource for Vote."""
    model = Vote


class ThreadRootResource(RootModelResource):
    """A create/list resource for Thread."""
    model = Thread

    def get(self, request, auth, *args, **kwargs):
        return self.model.objects.filter(**kwargs)[:20]


class ThreadResource(ModelResource):
    """A read/delete resource for Thread."""
    allowed_methods = ('GET', 'DELETE')
    anon_allowed_methods = ('GET',)
    model = Thread

    def get(self, request, auth, *args, **kwargs):
        slug = kwargs.get('section__slug')
        try:
            if not slug:
                instance = Thread.objects.get(**kwargs)
            else:
                op_post = Post.objects.get(pid=kwargs['id'],
                    thread__section__slug=kwargs['section__slug'])
                instance = op_post.thread
        except (Post.DoesNotExist, self.model.DoesNotExist):
            raise ResponseException(status.NOT_FOUND)
        res = {}
        for f in self.fields:
            res[f] = instance.__getattribute__(f)
        pf = [f for f in list(PostResource.fields)
            if isinstance(f, str) and f != 'files']
        res['posts'] = instance.posts().values(*pf)
        return res


class PostRootResource(RootModelResource):
    """A create/list resource for Post."""
    allowed_methods = anon_allowed_methods = ('GET', 'POST')
    form = PostForm
    model = Post

    def get(self, request, auth, *args, **kwargs):
        qs = self.model.objects.filter(**kwargs).reverse()
        if request.GET.get('html'):
            return qs.values('html')[:20]
        return qs[:20]

    def post(self, request, auth, content, *args, **kwargs):
        try:
            instance = validators.post(request, auth)
        except validators.ValidationError as e:
            return Response(status.BAD_REQUEST, {'detail': e})
        # django sends date with microseconds. We don't want it.
        instance.date = instance.date.strftime('%Y-%m-%d %H:%M:%S')
        url = 'http://127.0.0.1:8888/api/streamp/{0}'
        data = urllib.urlencode({'html': instance.html.encode('utf-8')})
        urllib2.urlopen(url.format(instance.thread.id), data)
        return Response(status.CREATED, instance)


class PostResource(ModelResource):
    """A read/delete resource for Post."""
    allowed_methods = anon_allowed_methods = ('GET', 'DELETE')
    model = Post

    def get(self, request, auth, *args, **kwargs):
        try:
            post = self.model.objects.get(**kwargs)
            if request.GET.get('html'):
                return {'html': post.html}
            return post
        except self.model.DoesNotExist:
            raise ResponseException(status.NOT_FOUND)

    def delete(self, request, auth, *args, **kwargs):
        """Deletes post."""
        try:
            post = self.model.objects.get(id=kwargs['id'])
        except self.model.DoesNotExist:
            raise ResponseException(status.NOT_FOUND)
        key = tools.key(request.GET['password'])
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
                posts = post.section().posts().filter(ip=post.ip)
                # remove threads
                op = posts.filter(is_op_post=True).values('pid', 'thread')
                template.rebuild_cache(slug, [i['pid'] for i in op])
                t = Thread.objects.filter(id__in=[i['thread'] for i in op])
                t.update(is_deleted=True)
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
    model = Section


class SectionResource(ModelResource):
    """A read resource for Section."""
    model = Section


class SectionGroupRootResource(RootModelResource):
    """A list resource for SectionGroup."""
    model = SectionGroup


class SectionGroupResource(ModelResource):
    """A read resource for SectionGroup."""
    model = SectionGroup


class FileRootResource(RootModelResource):
    """A list resource for File."""
    model = File


class FileResource(ModelResource):
    """A list resource for File."""
    allowed_methods = anon_allowed_methods = ('GET', 'DELETE')
    model = File

    def delete(self, request, auth, *args, **kwargs):
        """Deletes attachment."""
        try:
            file = self.model.objects.get(**kwargs)
        except self.model.DoesNotExist:
            raise ResponseException(status.NOT_FOUND)

        key = tools.key(request.GET['password'])
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
    model = FileType


class FileTypeResource(ModelResource):
    """A read resource for FileType."""
    model = FileType


class FileTypeGroupRootResource(RootModelResource):
    """A list resource for FileTypeGroup."""
    model = FileTypeGroup


class FileTypeGroupResource(ModelResource):
    """A read resource for FileTypeGroup."""
    model = FileTypeGroup
