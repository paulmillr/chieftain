#!/usr/bin/env python
# encoding: utf-8
"""
views.py

Created by Paul Bagwell on 2011-03-15.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from datetime import datetime
from hashlib import md5
from urllib import urlencode
from urllib2 import urlopen, URLError
from django.shortcuts import render
from django.contrib.gis.utils import GeoIP
from django.core.files import File as DjangoFile
from django.utils.translation import ugettext as _
from djangorestframework import status
from djangorestframework.resource import Resource
from djangorestframework.modelresource import ModelResource, RootModelResource
from djangorestframework.response import Response, ResponseException
from board.tools import (get_key, make_tripcode, parse_user_agent,
    handle_uploaded_file)
from board.models import *
from modpanel.views import is_mod

__all__ = [
    'ValidationError', 'api',
    'create_post', 'mod_delete_post',
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
    'FeedRootResource', 'FeedResource',
    'HideRootResource', 'HideResource',
]


class ValidationError(Exception):
    """This error is raised if content, created by user is sort of invalid.
    Note: we cannot use django.forms.ValidationError because we need
    to serialize error.
    """
    pass


def api(request):
    """Page, that contains some API examples."""
    return render(request, 'api.html')


def adapt_captcha(request):
    """Disables captcha, depending on some conditions.

    Captcha is disabled if:
    - User entered three valid captchas.
    - User is logged in.

    Returns post form. That form has or has not captcha field.
    """
    c = request.session.get('valid_captchas', 0)
    no_captcha = request.session.get('no_captcha', False)

    model = PostFormNoCaptcha if no_captcha else PostForm
    form = model(request.POST, request.FILES)
    if not form.is_valid():
        raise ValidationError(dict(form.errors))

    if request.user.is_authenticated():
        no_captcha = True
    else:
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
    return form


def create_post(request):
    """Makes various changes on new post creation.

       If there is no POST['thread'] specified, it will create
       new thread.
    """
    # TODO: divide this function into two smaller.
    # create_post doesn't need to be depended on request because we want
    # to reuse it in the wakaba converter
    new_thread = not request.POST.get('thread')
    with_files = bool(request.FILES.get('file'))
    logged_in = request.user.is_authenticated()
    # generate form, based on captcha settings
    form = adapt_captcha(request)
    # init Post model
    post = form.save(commit=False)
    post.date = datetime.now()
    post.is_op_post = new_thread
    post.ip = request.META.get('REMOTE_ADDR') or '127.0.0.1'
    post.password = get_key(post.password)
    if new_thread:
        section = Section.objects.get(slug=request.POST['section'])
        thread = Thread(section=section, bump=post.date)
    else:
        thread = Thread.objects.get(id=request.POST['thread'])
        if thread.is_closed and not logged_in:
            raise ValidationError(_('This thread is closed, '
                'you cannot post to it.'))
    section = thread.section
    section_is_feed = (thread.section.type == 3)

    if Wordfilter.objects.scan(post.message):
        raise ValidationError(_('Your post contains blacklisted word.'))
    if with_files:  # validate attachments
        file = request.FILES['file']
        allowed = section.allowed_filetypes()
        extension = allowed.get(file.content_type)
        if not extension:
            raise InvalidFileError(_('Invalid file type'))
        lim = section.filesize_limit
        if lim != 0 and file.size > lim:
            raise InvalidFileError(_('Too big file'))

        m = md5()
        for chunk in file.chunks():
            m.update(chunk)
        del chunk
        file_hash = m.hexdigest()
        # Check if this file already exists
        #if File.objects.filter(hash=file_hash).count() > 0:
        #    raise InvalidFileError(_('This file already exists'))
    else:
        if not post.message:
            raise ValidationError(_('Enter post message or attach '
                'a file to your post'))
        elif new_thread:
            if section.force_files:
                raise ValidationError(_('You need to '
                    'upload file to create new thread.'))
            elif section_is_feed and not logged_in:
                raise NotAuthenticatedError(_('Authentication required to '
                    'create threads in this section'))
    if (post.email.lower() != 'sage' and (new_thread or
        thread.posts().count() < section.bumplimit)):
        thread.bump = post.date
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
    elif '#' in post.poster:  # make tripcode
        s = post.poster.split('#')
        post.tripcode = make_tripcode(s.pop())
        post.poster = s[0]

    if not post.poster or section.anonymity:
        post.poster = section.default_name
    if post.email == 'mvtn'.encode('rot13'):  # easter egg o/
        s = u'\u5350'
        post.poster = post.email = post.topic = s * 10
        post.message = (s + u' ') * 50
    if section.type == 4:  # international
        post.data = {'country_code': GeoIP().country(post.ip)['country_code']}
    elif section.type == 5:  # show useragent
        ua = request.META['HTTP_USER_AGENT']
        parsed = parse_user_agent(ua)
        v = ''
        b = parsed.get('browser') or {'name': 'Unknown', 'version': ''}
        os = parsed.get('os') or {'name': 'Unknown'}
        if parsed.get('flavor'):
            v = parsed['flavor'].get('version') or ''
        post.data = {'useragent': {
            'name': b['name'],
            'version': b['version'],
            'os_name': os,
            'os_version': v,
            'raw': ua,
        }}
    if new_thread:
        thread.save(rebuild_cache=False)
        post.thread = thread
    post.pid = section.pid_incr()
    if with_files:
        file_type = FileType.objects.filter(extension=extension)[0]
        file_instance = File(
            name=file.name, type=file_type, hash=file_hash,
            file=DjangoFile(file), image_height=0, image_width=0
        )
        post.file = handle_uploaded_file(file_instance)
    post.save()
    thread.save()
    # add thread to user's feed
    feed_post_id = post.id if new_thread else thread.op_post.id
    request.session['feed'].add(int(feed_post_id))
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
        """Returns list of posts. If ?html option is specified, method
        will return only posts html without any other fields.
        TODO: implement pagination.
        """
        qs = self.model.objects.filter(**kwargs).reverse()[:20]
        if request.GET.get('html'):
            return qs.values('html')
        return qs

    def post(self, request, auth, content, *args, **kwargs):
        """Checks post for errors and returns new post instance."""
        try:
            instance = create_post(request)
        except ValidationError as e:
            raise ResponseException(status.BAD_REQUEST, {'detail': e.message})
        # django sends date with microseconds. We don't want it.
        instance.date = instance.date.strftime('%Y-%m-%d %H:%M:%S')
        url = 'http://127.0.0.1:8888/api/v1/streamp/{0}'
        data = urlencode({'html': instance.html.encode('utf-8')})
        try:
            urlopen(url.format(instance.thread.id), data)
        except URLError:
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
        """Gets post data. If ?html option is specified, method will return
        only post html without any other fields.
        """
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
        key = get_key(request.GET['password'])
        if post.password == key:
            post.remove()
        elif is_mod(request, post.section_slug()):
            mod_delete_post(request, post)
            post.remove()
        else:
            raise ResponseException(status.FORBIDDEN, content={
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
    """A list resource for random images."""
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

        key = get_key(request.GET['password'])
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
    """Base storage create/list/flush resource. Storage is a dict or set,
    located in the django session database.
    """
    allowed_methods = anon_allowed_methods = ('GET', 'POST', 'DELETE')
    storage_name = ''
    default = {}

    def get_data(self, request):
        return request.session[self.storage_name]

    def set_data(self, request, value):
        request.session[self.storage_name] = value

    def get(self, request, auth):
        return Response(status.OK, self.get_data(request))

    def delete(self, request, auth):
        """Clears whole storage."""
        self.set_data(request, self.default)
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
        data = self.get_data(request)
        try:
            value = int(content['value'])
        except (KeyError, TypeError):
            raise ResponseException(status.BAD_REQUEST)
        data.add(value)
        request.session.modified = True
        return Response(status.CREATED, data)


class StorageSetResource(StorageResource):
    """Storage read/delete resource, that uses set to store data."""
    default = set()

    def delete(self, request, auth, key):
        data = self.get_data(request)
        key = int(key)
        if key in data:
            data.remove(key)
            request.session.modified = True
        return Response(status.NO_CONTENT)


class StorageDictRootResource(StorageRootResource):
    """Storage create/list/flush resource, that uses dict to store data."""
    allowed_methods = anon_allowed_methods = ('GET', 'POST', 'DELETE')
    default = {}

    def post(self, request, auth, content):
        data = self.get_data(request)
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
        data = self.get_data(request)
        return Response(status.OK, data.get(key))

    def delete(self, request, auth, key):
        data = self.get_data(request)
        data.setdefault(key, None)
        request.session.modified = True
        return Response(status.NO_CONTENT)


class SettingRootResource(StorageDictRootResource):
    storage_name = 'settings'


class SettingResource(StorageDictResource):
    storage_name = 'settings'


class FeedRootResource(StorageSetRootResource):
    storage_name = 'feed'


class FeedResource(StorageSetResource):
    storage_name = 'feed'


class HideRootResource(StorageSetRootResource):
    storage_name = 'hidden'


class HideResource(StorageSetResource):
    storage_name = 'hidden'
