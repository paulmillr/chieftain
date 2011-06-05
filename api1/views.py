from urllib import urlencode
from urllib2 import urlopen, URLError
from hashlib import md5
from datetime import datetime

from django.shortcuts import render
from django.contrib.gis.utils import GeoIP
from django.core.files import File as DjangoFile
from django.utils.translation import ugettext as _

from djangorestframework import status
from djangorestframework.resource import Resource
from djangorestframework.response import Response, ResponseException
from djangorestframework.modelresource import ModelResource, RootModelResource

from board import models
from board.shortcuts import add_sidebar
from board.tools import (
    make_tripcode, parse_user_agent,
    get_key, handle_uploaded_file
)

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
    """
        The error raised when content created by user is invalid.
        NOTE: django.forms.ValidationError is unusable here
              because we need to serialize the exception.
    """
    pass


def api(request):
    """Render the page that contains some API usage examples."""
    return render(request, 'api.html', add_sidebar())


def adapt_captcha(request):
    """
        Disable captcha if ANY of these conditions are met:
            - user has entered three valid captchas in a row;
            - user is logged in.

        Returns the post form which MAY have a captcha field in it.
    """
    correct = request.session.get('valid_captchas', 0)
    no_captcha = request.session.get('no_captcha', False) \
              or request.user.is_authenticated()

    model = models.PostFormNoCaptcha if no_captcha else models.PostForm
    form = model(request.POST, request.FILES)

    if not form.is_valid():
        raise ValidationError(dict(form.errors))

    if no_captcha:
        correct -= 1
        request.session['no_captcha'] = bool(correct)
    else:
        correct += 1
        if correct == 3:
            request.session['no_captcha'] = True
            correct = 20
    request.session['valid_captchas'] = correct

    return form


def create_post(request):
    """
        Create a post from the form data the user has sent.
        This post will also begin a new thread if there were no
        'thread' field in the request.
    """
    user = request.user.is_authenticated() and request.user
    files = request.FILES.get('file', [])
    thread = request.POST.get('thread')
    section = request.POST['section'] if not thread else ''

    form = adapt_captcha(request)
    post = form.save(commit=False)
    return finish_post(
        post, user, thread, files, section,
        request.META.get('REMOTE_ADDR', '127.0.0.1'),
        request.META['HTTP_USER_AGENT'],
        request.session['feed']
    )


def finish_post(post, user, thread, files, section, ip, useragent, feed=None):
    # Set some common attributes.
    post.ip = ip
    post.date = datetime.now()
    post.password = get_key(post.password)
    post.is_op_post = not thread

    if models.Wordfilter.objects.scan(post.message):
        raise ValidationError(_('Your post contains blacklisted word.'))

    if not thread:
        section = models.Section.objects.get(slug=section)
        thread_o = models.Thread(section=section, bump=post.date)
    else:
        thread_o = models.Thread.objects.get(id=thread)
        section = thread_o.section
        if thread_o.is_closed and not user:
            raise ValidationError(
                _('This thread is closed, you cannot post to it.')
            )

    section_is_feed = section.type == 3

    if files:
        allowed = section.allowed_filetypes()
        extension = allowed.get(files.content_type)
        if not extension:
            raise InvalidFileError(_('Invalid file type'))

        lim = section.filesize_limit
        if files.size > lim > 0:
            raise InvalidFileError(_('Too big file'))

        m = md5()
        map(m.update, files.chunks())
        # TODO: Check if this file already exists.
        #       (Is this really needed at all?)
        #if models.File.objects.filter(hash=m.hexdigest()).count() > 0:
        #    raise InvalidFileError(_('This file already exists'))

        filetype = models.FileType.objects.filter(extension=extension)[0]
        post.file = handle_uploaded_file(
            models.File(
                name=files.name, type=filetype, hash=m.hexdigest(),
                file=DjangoFile(files), image_height=0, image_width=0
            )
        )
    else:
        if not post.message:
            raise ValidationError(
                _('Enter post message or attach a file to your post')
            )
        elif not thread:
            if section.force_files:
                raise ValidationError(
                    _('You need to upload file to create new thread.')
                )
            elif section_is_feed and not user:
                raise NotAuthenticatedError(
                    _(
                        'Authentication required to '
                        'create threads in this section'
                    )
                )

    # Bump the thread.
    if (post.email.lower() != 'sage'
    and thread and thread_o.posts().count() < section.bumplimit):
        thread_o.bump = post.date

    # Parse the signature.
    author, sign = (post.poster.split('!', 1) + [''])[:2]

    if sign == 'OP' and thread and post.password == thread_o.op_post.password:
        post.tripcode = '!OP'

    if sign == 'name' and user:
        if user.is_superuser:
            post.tripcode = '!{}'.format(user.username)
        else:
            post.tripcode = '!Mod'

    # Parse the tripcode.
    author, tripcode = (author.split('#', 1) + [''])[:2]
    if tripcode:
        post.tripcode = make_tripcode(tripcode)
    post.poster = author

    # Force-set the author name on some boards.
    if not post.poster or section.anonymity:
        post.poster = section.default_name

    if post.email == 'mvtn'.encode('rot13'):  # easter egg o/
        s = u'\u5350'
        post.poster = post.email = post.topic = s * 10
        post.message = (s + u' ') * 50

    if section.type == 4:
        # 4 == /int/ - International
        # Assign the country code to this post.
        post.data = {
            'country_code': models.GeoIP().country(post.ip)['country_code']
        }
    elif section.type == 5:
        # 5 == /bugs/ - Bugtracker
        # Display the user's browser name derived from HTTP User-Agent.
        parsed = parse_user_agent(useragent)
        browser = parsed.get('browser', {'name': 'Unknown', 'version': ''})
        platform = parsed.get('os', {'name': 'Unknown'})

        browser['os_name'] = platform['name']
        browser['os_version'] = parsed.get('flavor', {}).get('version', '')
        browser['raw'] = useragent
        post.data = {'useragent': browser}

    if not thread:
        thread_o.save(rebuild_cache=False)
        post.thread = thread_o
    post.pid = section.pid_incr()
    post.save()
    thread_o.save()

    if feed is not None:
        thread_id = int(thread or post.id)
        feed.add(thread_id)
    return post


def mod_delete_post(request, post):
    if request.GET.get('ban_ip'):
        reason = request.GET.get('ban_reason')
        if not reason:
            raise ResponseException(status.BAD_REQUEST,
                {'detail': _('You need to enter ban reason')}
            )
        ip = DeniedIP(ip=post.ip, reason=r, by=request.user)
        ip.save()

    if request.GET.get('delete_all'):
        posts = post.section().posts().filter(ip=post.ip)
        op = posts.filter(is_op_post=True).values('pid', 'thread')
        t = models.Thread.objects.filter(id__in=[i['thread'] for i in op])
        t.update(is_deleted=True)

        for p in posts:
            p.remove()


class PollRootResource(RootModelResource):
    """A list resource for Poll."""
    model = models.Poll


class PollResource(ModelResource):
    """A read resource for Poll."""
    model = models.Poll


class ChoiceRootResource(RootModelResource):
    """A list resource for Choice."""
    model = models.Choice


class ChoiceResource(ModelResource):
    """A read resource for Choice."""
    model = models.Choice


class VoteRootResource(RootModelResource):
    """A list/create resource for Vote."""
    allowed_methods = anon_allowed_methods = ('GET', 'POST')
    model = models.Vote

    def post(self, request, auth, *args, **kwargs):
        try:
            choice = models.Choice.objects.get(id=request.POST['choice'])
        except Choice.DoesNotExist:
            raise ResponseException(status.NOT_FOUND)
        ip = request.META['REMOTE_ADDR']
        check = models.Vote.objects.filter(ip=ip, poll=choice.poll)
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
    model = models.Vote


class ThreadRootResource(RootModelResource):
    """A create/list resource for Thread."""
    model = models.Thread

    def get(self, request, auth, *args, **kwargs):
        return self.model.objects.filter(**kwargs)[:20]


class ThreadResource(ModelResource):
    """A read/delete resource for Thread."""
    allowed_methods = ('GET', 'DELETE')
    anon_allowed_methods = ('GET',)
    model = models.Thread

    def get(self, request, auth, *args, **kwargs):
        slug = kwargs.get('section__slug')
        try:
            if not slug:
                instance = models.Thread.objects.get(**kwargs)
            else:
                op_post = models.Post.objects.get(pid=kwargs['id'],
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
    form = models.PostFormNoCaptcha
    model = models.Post

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
        url = 'http://127.0.0.1:8888/api/1.0/streamp/{0}'
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
    model = models.Post

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
    model = models.Section


class SectionResource(ModelResource):
    """A read resource for Section."""
    model = models.Section


class SectionGroupRootResource(RootModelResource):
    """A list resource for SectionGroup."""
    model = models.SectionGroup


class SectionGroupResource(ModelResource):
    """A read resource for SectionGroup."""
    model = models.SectionGroup


class FileRootResource(RootModelResource):
    """A list resource for File."""
    model = models.File


class RandomImageRootResource(RootModelResource):
    """A list resource for random images."""
    model = models.File
    fields = ('id', 'name', 'type', 'size',
        'image_width', 'image_height', 'hash', 'file', 'thumb')

    def get(self, request, auth, *args, **kwargs):
        count = kwargs.get('count', 3)
        return self.model.objects.random_images()[:count]


class FileResource(ModelResource):
    """A list resource for File."""
    allowed_methods = anon_allowed_methods = ('GET', 'DELETE')
    model = models.File

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
    model = models.FileType


class FileTypeResource(ModelResource):
    """A read resource for FileType."""
    model = models.FileType


class FileTypeGroupRootResource(RootModelResource):
    """A list resource for FileTypeGroup."""
    model = models.FileTypeGroup


class FileTypeGroupResource(ModelResource):
    """A read resource for FileTypeGroup."""
    model = models.FileTypeGroup


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
            key = content['key']
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
        if key in data:
            del data[key]
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
