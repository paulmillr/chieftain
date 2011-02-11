#!/usr/bin/env python
# encoding: utf-8
"""
models.py

Created by Paul Bagwell on 2011-01-13.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
import re
from datetime import datetime
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db import models
from django.forms import ModelForm, CharField, IntegerField
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from hashlib import sha1
from django.core.exceptions import ImproperlyConfigured
from ipcalc import Network
from board import fields


__all__ = [
    'cache', 'render_to_string',
    'DAY', 'cached', 'InsufficientRightsError', 'InvalidKeyError',
    'PostManager', 'SectionManager', 'SectionGroupManager', 'Thread', 'Post',
    'File', 'FileCategory', 'FileType', 'Section', 'SectionGroup', 'User',
    'PostForm', 'PostFormNoCaptcha', 'ThreadForm', 'DeniedIP', 'AllowedIP',
]

DAY = 86400  # seconds in day
MEGABYTE = 2 ** 20
SECTION_TYPES = (
    (1, _('Default')),
    (2, _('No images')),
    (3, _('Feed')),  # Users, that don't have accounts can't create threads
    (4, _('Premodded')),  # Each thread needs to be approved
    (5, _('Chat')),
)


def cached(seconds=900):
    """
        Cache the result of a function call for the specified number of
        seconds, using Django's caching mechanism.
    """
    def doCache(f):
        def x(*args, **kwargs):
                key = sha1(f.__module__ + f.__name__ +
                    str(args) + str(kwargs)).hexdigest()
                result = cache.get(key)
                if result is None:
                    result = f(*args, **kwargs)
                    cache.set(key, result, seconds)
                return result
        return x
    return doCache


class InsufficientRightsError(Exception):
    """Raises if user has insufficient rights for current operation."""
    pass


class InvalidKeyError(Exception):
    """Raises if user has entered invalid modkey or deletion password."""
    pass


class PostManager(models.Manager):
    @cached(3 * DAY)
    def by_section(self, slug, pid):
        """Gets post by its pid and section slug."""
        try:
            post = self.get(thread__section__slug=slug, pid=pid)
        except Post.DoesNotExist as e:
            raise e
        else:
            return post


class SectionManager(models.Manager):
    @cached(DAY)
    def sections(self):
        return Section.objects.all().order_by('slug')


class SectionGroupManager(models.Manager):
    """Manager for SectionGroup."""
    @cached(DAY)
    def sections(self):
        """
           Gets list of board sections.
           We're not using QuerySet because they cannot be cached.
        """
        groups = SectionGroup.objects.all().order_by('order')
        data = []  # http://goo.gl/CpPq6
        for group in groups:
            d = {
                'id': group.id,
                'name': group.name,
                'order': group.order,
                'is_hidden': group.is_hidden,
                'sections': list(group.section_set.values())
            }
            data.append(d)
        return data


class Thread(models.Model):
    """Groups of posts."""
    section = models.ForeignKey('Section')
    bump = models.DateTimeField(blank=True, db_index=True,
        verbose_name=_('Thread bump date'))
    is_deleted = models.BooleanField(default=False,
        verbose_name=_('Thread is deleted'))
    is_pinned = models.BooleanField(default=False,
        verbose_name=_('Thread is pinned'))
    is_closed = models.BooleanField(default=False,
        verbose_name=_('Thread is closed'))
    html = models.TextField(blank=True, verbose_name=_('Thread html'))

    @property
    def posts_html(self):
        return self.post_set.filter(is_deleted=False).values('html')

    def count(self):
        lp = 5
        ps = self.post_set.filter(is_deleted=False)
        stop = ps.count()
        if stop <= lp:  # if we got thread with less posts than lp
            return {'total': stop, 'skipped': 0, 'skipped_files': 0}
        else:
            start = stop - lp
            return {
                'total': stop, 'start': start, 'stop': stop,
                'skipped': start - 1,
                'skipped_files': ps.filter(file_count__gt=0).count()
            }

    @property
    def op_post(self):
        return self.post_set.all()[0]

    @property
    def last_posts(self):
        c = self.count()
        s = self.post_set.filter(is_deleted=False)
        all = s.all()
        if not c['skipped']:
            return all
        else:  # select first one and last 5 posts
            start, stop = c['start'], c['stop']
            return [s.all()[0]] + list(all[start:stop])

    def remove(self):
        """Deletes thread."""
        self.post_set.all().update(is_deleted=True)
        self.is_deleted = True
        self.save()

    def refresh_cache(self):
        """Regenerates cache of OP-post and last 5."""
        self.html = render_to_string('section_thread.html', {'thread': self})

    def save(self, no_cache_rebuild=False):
        """Saves thread and rebuilds cache."""
        if not no_cache_rebuild:
            self.refresh_cache()
        super(self.__class__, self).save()

    def __unicode__(self):
        return unicode(self.id)

    class Meta:
        verbose_name = _('Thread')
        verbose_name_plural = _('Threads')
        get_latest_by = 'bump'
        ordering = ['-bump']


class Post(models.Model):
    """Represents post."""
    pid = models.PositiveIntegerField(blank=True, verbose_name=_('PID'))
    thread = models.ForeignKey('Thread', blank=True, null=True,
        verbose_name=_('Post thread'))
    is_op_post = models.BooleanField(default=False,
        verbose_name=_('Post is op post'))
    date = models.DateTimeField(default=datetime.now, blank=True,
        verbose_name=_('Post bump date'))
    is_deleted = models.BooleanField(default=False,
        verbose_name=_('Post is deleted'))
    file_count = models.SmallIntegerField(default=0,
        verbose_name=_('Post file count'), blank=True)
    ip = models.IPAddressField(verbose_name=_('Post ip'), blank=True)
    poster = models.CharField(max_length=32, blank=True,
        verbose_name=_('Post poster'))
    tripcode = models.CharField(max_length=32, blank=True,
        verbose_name=_('Post tripcode'))
    email = models.CharField(max_length=32, blank=True,
        verbose_name=_('Post email'))
    topic = models.CharField(max_length=48, blank=True,
        verbose_name=_('Post topic'))
    password = models.CharField(max_length=64, blank=True,
        verbose_name=_('Post password'))
    message = models.TextField(verbose_name=_('Post message'))
    html = models.TextField(blank=True, verbose_name=_('Post html'))
    objects = PostManager()
    
    @cached(DAY)
    @property
    def section(self):
        return self.thread.section.slug

    def remove(self):
        """Deletes post."""
        if self.is_op_post:
            self.thread.remove()
        self.is_deleted = True
        self.save()
        self.thread.save()

    def refresh_cache(self):
        """Regenerates html cache of post."""
        self.html = render_to_string('post.html', {'post': self})

    def save(self):
        """Overload of default save method."""
        if not self.id:
            super(self.__class__, self).save()
        self.refresh_cache()
        super(self.__class__, self).save()

    def __unicode__(self):
        return '{slug}/{pid}'.format(slug=self.thread.section.slug, pid=self.pid)

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        get_latest_by = 'pid'
        ordering = ['pid']


class File(models.Model):
    """Represents files at the board."""
    post = models.ForeignKey('Post', verbose_name=_('File post'))
    name = models.CharField(max_length=64,
        verbose_name=_('File original name'))
    mime = models.ForeignKey('FileType', verbose_name=_('File MIME'))
    size = models.PositiveIntegerField(verbose_name=_('file_size'))
    is_deleted = models.BooleanField(default=False,
        verbose_name=_('File is deleted'))
    image_width = models.PositiveSmallIntegerField(blank=True,
        verbose_name=_('File image width'))
    image_height = models.PositiveSmallIntegerField(blank=True,
        verbose_name=_('File image height'))
    #meta = models.TextField()
    hash = models.CharField(max_length=32, blank=True,
        verbose_name=_('File hash'))
    file = models.FileField(upload_to='test/{}',
        verbose_name=_('File location'))

    def __unicode__(self):
        return self.post

    class Meta:
        verbose_name = _('File')
        verbose_name_plural = _('Files')


class FileCategory(models.Model):
    """Category of files"""
    name = models.CharField(max_length=32,
        verbose_name=_('File category name'))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('File category')
        verbose_name_plural = _('File categories')


class FileType(models.Model):
    """File type"""
    extension = models.CharField(max_length=10, unique=True,
        verbose_name=_('File type extension'))
    mime = models.CharField(max_length=250, blank=False,
        verbose_name=_('File type MIME'))
    category = models.ForeignKey('FileCategory',
        verbose_name=_('File type category'))

    def __unicode__(self):
        return self.extension

    class Meta:
        verbose_name = _('File type')
        verbose_name_plural = _('File types')


class Section(models.Model):
    """Board section"""
    slug = models.SlugField(max_length=5, unique=True,
        verbose_name=_('Section slug'))
    name = models.CharField(max_length=64,
        verbose_name=_('Section name'))
    description = models.TextField(blank=False,
        verbose_name=_('Section description'))
    type = models.PositiveSmallIntegerField(default=1, choices=SECTION_TYPES,
        verbose_name=_('Section type'))
    group = models.ForeignKey('SectionGroup',
        verbose_name=_('Section group'))
    filesize_limit = models.PositiveIntegerField(default=MEGABYTE * 5,
        verbose_name=_('Section filesize limit'))
    anonymity = models.BooleanField(default=False,
        verbose_name=_('Section force anonymity'))
    default_name = models.CharField(max_length=64, default='Anonymous',
        verbose_name=_('Section default poster name'))
    filetypes = models.ManyToManyField(FileCategory,
        verbose_name=_('Section allowed filetypes'))
    bumplimit = models.PositiveSmallIntegerField(default=500,
        verbose_name=_('Section bumplimit'))
    threadlimit = models.PositiveSmallIntegerField(default=10,
        verbose_name=_('Section thread limit'))
    objects = SectionManager()

    def page_threads(self, page=1):
        onpage = 20
        threads = Paginator(self.thread_set.filter(is_deleted=False), onpage)
        return threads.page(page)

    @property
    def key(self):
        """Memcached key name."""
        return 'section_last_{slug}'.format(slug=self.slug)

    @property
    def pid(self):
        """Gets section last post PID."""
        return cache.get(self.key) or self.refresh_cache()

    @pid.setter
    def pid(self, value):
        """Sets section last post PID cache to value."""
        cache.set(self.key, value)
        return value

    def pid_incr(self):
        """Increments section last post PID cache by 1."""
        try:
            return cache.incr(self.key)
        except ValueError:
            self.refresh_cache()
        return cache.incr(self.key)

    def refresh_cache(self):
        """Refreshes cache of section last post PID."""
        try:
            pid = Post.objects.filter(thread__section=self.id).latest().pid
        except Post.DoesNotExist:  # no posts in section
            pid = 0
        self.pid = pid
        return pid

    def __unicode__(self):
        return self.slug

    class Meta:
        verbose_name = _('Section')
        verbose_name_plural = _('Sections')


class SectionGroup(models.Model):
    """Group of board sections. Example: [b / d / s] [a / aa] """
    name = models.CharField(max_length=64, blank=False,
        verbose_name=_('Section group name'))
    order = models.SmallIntegerField(verbose_name=_('Section group order'))
    is_hidden = models.BooleanField(default=False, verbose_name=_('Is hidden'))
    objects = SectionGroupManager()

    def __unicode__(self):
        return unicode(self.name) + ', ' + unicode(self.order)

    class Meta:
        verbose_name = _('Section group')
        verbose_name_plural = _('Section groups')


class User(models.Model):
    """User (moderator etc.)"""
    username = models.CharField(max_length=32, unique=True,
        verbose_name=_('User name'))
    password = models.CharField(max_length=64,
        verbose_name=_('User password'))
    # sections, modded by user
    sections = models.ManyToManyField('Section', blank=False,
        verbose_name=_('User owned sections'))

    def __unicode__(self):
        return self.username

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')


class IP(models.Model):
    """Abstract base class for all ban classes."""
    ip = models.CharField(_('IP network'), max_length=18,
            help_text=_('Either IP address or IP network specification'))

    def __unicode__(self):
        return self.ip

    def network(self):
        return Network(self.ip)

    class Meta:
        abstract = True


class DeniedIP(IP):
    """Used for bans."""
    class Meta:
        verbose_name = _('Denied IP')
        verbose_name_plural = _('Denied IPs')


class AllowedIP(IP):
    """Used for bans."""
    class Meta:
        verbose_name = _('Allowed IP')
        verbose_name_plural = _('Allowed IPs')


class PostFormNoCaptcha(ModelForm):
    """Post form with no captcha.

       Used for disabling double requests to api server.
    """
    section = IntegerField(required=False)

    class Meta:
        model = Post


class PostForm(PostFormNoCaptcha):
    """Simple post form."""
    captcha = fields.ReCaptchaField(required=False)
    recaptcha_challenge_field = CharField(required=False)
    recaptcha_response_field = CharField(required=False)


class ThreadForm(ModelForm):
    class Meta:
        model = Thread
