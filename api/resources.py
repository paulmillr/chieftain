#!/usr/bin/env python
# encoding: utf-8
"""
resources.py

Created by Paul Bagwell on 2011-02-03.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
import urllib
import urllib2
from django import forms
from django.contrib.gis.utils import GeoIP
from django.utils.translation import ugettext as _
from djangorestframework import status
from djangorestframework.resource import Resource
from djangorestframework.modelresource import ModelResource, RootModelResource
from djangorestframework.response import Response, ResponseException
from board import tools
from api import emitters
from board.models import *
from modpanel.views import is_mod

__all__ = (
    'Resource', 'ModelResource', 'RootModelResource',
    'PollRootResource', 'PollResource',
    'ChoiceRootResource', 'ChoiceResource',
    'VoteRootResource', 'VoteResource',
    'ThreadRootResource', 'ThreadResource',
    'PostRootResource', 'PostResource',
    'SectionRootResource', 'SectionResource',
    'FileRootResource', 'FileResource',
    'RandomImageRootResource',
    'FileTypeRootResource', 'FileTypeResource',
    'FileTypeGroupRootResource', 'FileTypeGroupResource',
    'SectionGroupRootResource', 'SectionGroupResource',
    'StorageRootResource', 'StorageResource',
    'StorageDictRootResource', 'StorageDictResource',
    'StorageSetRootResource', 'StorageSetResource',
    'SettingRootResource', 'SettingResource',
    'BookmarkRootResource', 'BookmarkResource',
    'HideRootResource', 'HideResource',
)


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


def validate_post(request):
    logged_in = request.user.is_authenticated()

    # adaptive captcha check
    c = request.session.get('valid_captchas', 0)
    no_captcha = request.session.get('no_captcha', False)
    if logged_in:
        no_captcha = True
    f = PostFormNoCaptcha if no_captcha else PostForm
    form = f(request.POST, request.FILES)
    if not form.is_valid():
        raise forms.ValidationError(form.errors)
    post = form.save(commit=False)
    post.ip = request.META.get('REMOTE_ADDR') or '127.0.0.1'
    thread = post.thread
    new_thread = post.is_op_post

    if no_captcha:
        c -= 1  # decrease allowed no-captcha posts
        if c == 0:
            request.session['no_captcha'] = False
    else:
        c += 1  # increase valid captchas counter
        if c == 3:
            request.session['no_captcha'] = True
            c = 20
    request.session['valid_captchas'] = c

    if thread.is_closed and not logged_in:
        raise forms.ValidationError(_('This thread is closed, '
            'you cannot post to it.'))
    if thread.section.type == 3:  # feed
        if post.is_op_post and not logged_in:
            raise forms.ValidationError(_('Authentication required to create '
                'threads in this section'))
    elif thread.section.type == 4:  # international
        post.data = {'country_code': GeoIP().country(post.ip)['country_code']}
    elif thread.section.type == 5:  # show useragent
        ua = request.META['HTTP_USER_AGENT']
        parsed = tools.parse_user_agent(ua)
        v = ''
        b = parsed.get('browser') or {'name': 'Unknown', 'version': ''}
        os = parsed.get('os') or {'name': 'Unknown'}
        if parsed.get('flavor'):
            v = parsed['flavor'].get('version')
        post.data = {'useragent': {
            'name': b['name'],
            'version': b['version'],
            'os_name': os,
            'os_version': v,
            'raw': ua,
        }}
    if '!' in post.poster:  # make user signature
        if ('!OP' in post.poster and not new_thread and
            post.password == thread.op_post.password):
            post.poster = ''
            post.tripcode = '!OP'
        elif '!name' in post.poster and logged_in:
            post.poster = ''
            if request.user.is_superuser:
                username = '!{0}'.format(request.user.username)
            else:
                username = '!Mod'
            post.tripcode = username
    if new_thread:
        thread.save(rebuild_cache=False)
        post.thread = thread
    post.pid = thread.section.pid_incr()
    if post.file:
        post.save(rebuild_cache=False)
        tools.handle_uploaded_file(file, ext)
    post.save()
    thread.save()
    return post


def mod_delete_post(request, post):
    if request.GET.get('ban_ip'):
        r = request.GET.get('ban_reason')
        if not r:
            raise ResponseException(status.BAD_REQUEST, {
                'detail': _('You need to enter ban reason')})
        d = DeniedIP(ip=post.ip, reason=r, by=request.user)
        d.save()
    if request.GET.get('delete_all'):
        slug = post.section_slug()
        posts = post.section().posts().filter(ip=post.ip)
        # remove threads
        op = posts.filter(is_op_post=True).values('pid', 'thread')
        t = Thread.objects.filter(id__in=[i['thread'] for i in op])
        t.update(is_deleted=True)
        for p in posts:
            p.remove()


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
        res = {f: getattr(instance, f) for f in self.fields}
        # remove nested fields
        fields = [f for f in list(PostResource.fields)
            if isinstance(f, str) and f != 'files']
        res['posts'] = instance.posts().values(*fields)
        return res


class PostRootResource(RootModelResource):
    """A create/list resource for Post."""
    allowed_methods = anon_allowed_methods = ('GET', 'POST')
    form = PostFormNoCaptcha
    model = Post

    def get(self, request, auth, *args, **kwargs):
        qs = self.model.objects.filter(**kwargs).reverse()
        if request.GET.get('html'):
            return qs.values('html')[:20]
        return qs[:20]

    def post(self, request, auth, content, *args, **kwargs):
        try:
            instance = validate_post(request)
        except forms.ValidationError as e:
            return Response(status.BAD_REQUEST, {'detail': e})
        # django sends date with microseconds. We don't want it.
        instance.date = instance.date.strftime('%Y-%m-%d %H:%M:%S')
        url = 'http://127.0.0.1:8888/api/streamp/{0}'
        data = urllib.urlencode({'html': instance.html.encode('utf-8')})
        try:
            urllib2.urlopen(url.format(instance.thread.id), data)
        except urllib2.URLError:
            raise ResponseException(status.INTERNAL_SERVER_ERROR, {
                'detail': u'{0}: {1}'.format(
                    _('Server error'), _('can\'t refresh messages')
                )
            })
        self.model.allowed_fields.append('html')
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
        elif is_mod(request, post.section_slug()):
            mod_delete_post(request, post)
            post.remove()
        else:
            return Response(status.FORBIDDEN, content={
                'detail': u'{0}{1}. {2}'.format(
                    _('Error on deleting post #'), post.pid,
                    _('Password mismatch')
                )
            })
        return Response(status.NO_CONTENT)


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


class RandomImageRootResource(RootModelResource):
    model = File
    fields = ('id', 'name', 'type', 'size',
        'image_width', 'image_height', 'hash', 'file', 'thumb')

    def get(self, request, auth, *args, **kwargs):
        count = kwargs.get('count', 3)
        return self.model.objects.random_images()[:count]


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
        if file.post.password == key:
            file.remove()
        elif is_mod(request, file.post.section_slug()):
            mod_delete_post(request, file.post)
            file.remove()
        else:
            raise ResponseException(status.FORBIDDEN, content={
                'detail': u'{0}{1}. {2}'.format(
                    _('Error on deleting file #'), file.post.pid,
                    _('Password mismatch')
                )
            })
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


class StorageRootResource(Resource):
    """Base storage create/list/flush resource."""
    allowed_methods = anon_allowed_methods = ('GET', 'POST', 'DELETE')
    storage_name = ''
    default = {}

    def setdefault(self, session):
        return session.setdefault(self.storage_name, self.default)

    def get(self, request, auth):
        data = self.setdefault(request.session)
        return Response(status.OK, data)

    def delete(self, request, auth):
        """Clears whole storage."""
        data = self.setdefault(request.session)
        request.session[self.storage_name] = self.default
        return Response(status.NO_CONTENT)


class StorageResource(StorageRootResource):
    """Base storage read/delete resource."""
    allowed_methods = anon_allowed_methods = ('GET', 'DELETE')

    def get(self, request, auth, key):
        raise ResponseException(status.NOT_IMPLEMENTED)


class StorageSetRootResource(StorageRootResource):
    """Storage create/list/flush resource, that uses set to store data."""
    default = set()

    def post(self, request, auth, content):
        data = self.setdefault(request.session)
        key = int(content['key'])
        data.add(key)
        request.session.modified = True
        return Response(status.CREATED, data)


class StorageSetResource(StorageResource):
    """Storage read/delete resource, that uses set to store data."""
    default = set()

    def delete(self, request, auth, key):
        data = self.setdefault(request.session)
        key = int(key)
        if key in data:
            data.remove(key)
            request.session.modified = True
        return Response(status.NO_CONTENT)


class StorageDictRootResource(StorageResource):
    """Storage create/list/flush resource, that uses dict to store data."""
    allowed_methods = anon_allowed_methods = ('GET', 'POST', 'DELETE')
    default = {}

    def post(self, request, auth, content):
        data = setdefault(request.session)
        try:
            key = int(content['key'])
            value = content['value']
        except KeyError:
            raise ResponseException(status.BAD_REQUEST)
        data[key] = value
        request.session.modified = True
        return Response(status.CREATED, data)


class StorageDictResource(StorageResource):
    """Storage read/delete resource, that uses dict to store data."""
    allowed_methods = anon_allowed_methods = ('GET', 'DELETE')
    default = {}

    def get(self, request, auth, key):
        data = setdefault(request.session)
        return Response(status.OK, data.get(key))

    def delete(self, request, auth, key):
        if key in data:
            data[key] = None
        request.session.modified = True
        return Response(status.NO_CONTENT)


class SettingRootResource(StorageDictRootResource):
    storage_name = 'settings'


class SettingResource(StorageDictResource):
    storage_name = 'settings'


class BookmarkRootResource(StorageSetRootResource):
    storage_name = 'bookmarks'


class BookmarkResource(StorageSetResource):
    storage_name = 'bookmarks'


class HideRootResource(StorageRootResource):
    storage_name = 'hidden'


class HideResource(StorageSetResource):
    storage_name = 'hidden'
