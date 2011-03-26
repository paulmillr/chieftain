#!/usr/bin/env python
# encoding: utf-8
"""
models.py

Created by Paul Bagwell on 2011-01-13.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from collections import Counter
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.syndication.views import Feed
from django.core.cache import cache
from django.db import models, connection
from django.db.models.aggregates import Count
from django.forms import ModelForm, CharField, FileField
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from hashlib import sha1
from ipcalc import Network
from board import fields, template, tools


__all__ = [
    'DAY', 'cached',
    'PostManager', 'SectionManager', 'SectionGroupManager',
    'Poll', 'Choice', 'Vote',
    'Thread', 'Post', 'File', 'FileTypeGroup', 'FileType', 'Section',
    'SectionGroup', 'UserProfile', 'PostForm', 'PostFormNoCaptcha',
    'SectionFeed', 'ThreadFeed', 'DeniedIP', 'Wordfilter',
]

DAY = 86400  # seconds in day
MEGABYTE = 2 ** 20
SECTION_TYPES = (
    (1, _('Default')),
#    (2, _('Premodded')),
    (3, _('News')),
    (4, _('International')),
    (5, _('Software')),
#    (5, _('Private')),
#    (6, _('Chat')),
)


def get_file_path(base):
    """Builds path to stored static files. Used in File class."""
    def closure(instance, filename):
        ip = instance.post
        return '{base}/{slug}/{pid}.{ext}'.format(
            base=base, slug=ip.section_slug(), thread=ip.thread,
            pid=ip.pid, ext=instance.type.extension
        )
    return closure


def cached(seconds=900, key=None):
    """Cache the result of a function call."""
    def do_cache(f):
        def closure(*args, **kwargs):
            if key:
                cache_key = key
            else:
                cache_key = sha1(f.__module__ + f.__name__ +
                    str(args) + str(kwargs)).hexdigest()
            result = cache.get(cache_key)
            if result is None:
                result = f(*args, **kwargs)
                cache.set(cache_key, result, seconds)
            return result
        return closure
    return do_cache


class ThreadManager(models.Manager):
    def get_query_set(self):
        return super(ThreadManager, self).get_query_set().filter(
            is_deleted=False)

    def post_count(self):
        return self.annotate(Count('post')).order_by('-post__count')


class DeletedThreadManager(models.Manager):
    def get_query_set(self):
        return super(DeletedThreadManager, self).get_query_set().filter(
            is_deleted=True)


class PostManager(models.Manager):
    def get_query_set(self):
        return super(PostManager, self).get_query_set().filter(
            is_deleted=False)

    def popular(self, limit=10):
        """Gets most popular board threads.

        Popularity is calculated by thread post count.
        Each section can have only two popular threads.
        This method returns list of post dicts with 'description' value,
        that contains post title / text / link.
        """
        # Aggregate thread posts.
        threads = Thread.objects.post_count().order_by('-post__count').values(
            'id', 'section', 'post__count')[:limit * 10]
        thread_ids = []
        counter = Counter()

        # Select two threads from each section.
        for t in threads:
            if len(thread_ids) > limit:
                break
            if counter[t['section']] < 2:
                thread_ids.append(t['id'])
                counter[t['id']] += 1

        # Get post information.
        posts = Post.objects.filter(thread__in=thread_ids,
            is_op_post=True).values('thread__section__name',
            'thread__section__slug', 'pid', 'topic', 'message'
        )[:limit]

        # Filter post information.
        return (tools.make_post_description(p) for p in posts)


class DeletedPostManager(models.Manager):
    def get_query_set(self):
        return super(DeletedPostManager, self).get_query_set().filter(
            is_deleted=True)


class FileManager(models.Manager):
    def get_query_set(self):
        return super(FileManager, self).get_query_set().filter(
            is_deleted=False)

    def random_images(self):
        return self.filter(image_width__gt=200).order_by('?')


class DeletedFileManager(models.Manager):
    def get_query_set(self):
        return super(DeletedFileManager, self).get_query_set().filter(
            is_deleted=True)


class SectionManager(models.Manager):
    @cached(DAY)
    def sections(self):
        return self.order_by('slug')


class SectionGroupManager(models.Manager):
    """Manager for SectionGroup."""
    @cached(DAY, 'sections')
    def sections(self):
        """
           Gets list of board sections.
           We're not using QuerySet because they cannot be cached.
        """
        data = []
        sections = list(Section.objects.all().values())
        for g in self.order_by('order').values():
            g['sections'] = [s for s in sections if s['group_id'] == g['id']]
            data.append(g)
        return data


class WordfilterManager(models.Manager):
    """Manager for Wordfilter."""

    def words(self):
        return tools.take_first(self.values_list('word'))

    def scan(self, message):
        return any(word in message for word in self.words())


class Poll(models.Model):
    """Thread polls."""
    question = models.CharField(max_length=200, verbose_name=_('Question'))
    expires = models.DateTimeField(verbose_name=_('Expire date'))

    allowed_fields = ('id', 'question', ('choices', ('name', 'vote_count')))

    def choices(self):
        return self.choice_set.all()

    def get_vote_data(self, ip):
        f = Vote.objects.filter(ip=ip, poll=self)
        if not f:
            return False
        return f.get()

    def __unicode__(self):
        return self.question

    class Meta:
        verbose_name = _('Poll')
        verbose_name_plural = _('Polls')


class Choice(models.Model):
    """Thread poll answers."""
    name = models.CharField(max_length=100, verbose_name=_('Choice name'))
    poll = models.ForeignKey('Poll', verbose_name=_('Poll'))
    vote_count = models.PositiveIntegerField(default=0,
        verbose_name=_('Vote count'))

    allowed_fields = ('id', 'name', 'vote_count', ('poll', ('question',)))

    def __unicode__(self):
        return u'{0} - {1}'.format(self.poll, self.name)

    class Meta:
        verbose_name = _('Poll choice')
        verbose_name_plural = _('Poll choices')


class Vote(models.Model):
    """Thread poll votes."""
    poll = models.ForeignKey('Poll', blank=True, null=True,
        verbose_name=_('Poll'))
    choice = models.ForeignKey('Choice', verbose_name=_('Choice'))
    ip = models.IPAddressField(blank=True, verbose_name=_('IP'))

    allowed_fields = ('id', 'choice')

    def __unicode__(self):
        return u'{0}, {1}'.format(self.choice, self.ip)

    class Meta:
        verbose_name = _('Poll vote')
        verbose_name_plural = _('Poll votes')


class Thread(models.Model):
    """Groups of posts."""
    section = models.ForeignKey('Section')
    bump = models.DateTimeField(blank=True, db_index=True,
        verbose_name=_('Bump date'))
    is_deleted = models.BooleanField(default=False,
        verbose_name=_('Is deleted'))
    is_pinned = models.BooleanField(default=False,
        verbose_name=_('Is pinned'))
    is_closed = models.BooleanField(default=False,
        verbose_name=_('Is closed'))
    poll = models.ForeignKey('Poll', blank=True, null=True,
        verbose_name=_('Poll'))
    html = models.TextField(blank=True, verbose_name=_('HTML cache'))
    objects = ThreadManager()
    deleted_objects = DeletedThreadManager()

    allowed_fields = (
        'id', 'section_id', 'bump', 'is_pinned',
        'is_closed', 'html',
    )

    def posts(self):
        """Returns thread posts."""
        return self.post_set.all()

    def posts_html(self):
        return self.posts().values('html', 'ip')

    #@cached(1)
    def count(self):
        """Returns dict, that contains info about thread files and posts."""
        lp = 5
        ps = self.posts()
        stop = ps.count()
        if stop <= lp:  # if we got thread with less posts than lp
            return {'total': stop, 'skipped': 0, 'skipped_files': 0}
        else:
            start = stop - lp
            skipped_ids = tools.take_first(ps[:stop - lp].values_list('id'))
            skipped_ids.pop(0)  # remove first post
            return {
                'total': stop,
                'start': start,
                'stop': stop,
                'skipped': start - 1,
                'skipped_files': ps.filter(id__in=skipped_ids,
                    file_count__gt=0).count()
            }

    @property
    def op_post(self):
        if not self.is_deleted:
            post_set = self.post_set
        else:
            post_set = Post.deleted_objects.filter(thread=self)
        return post_set.filter(is_op_post=True).get()

    def un_lp(self, offset, limit):
        fields = ('thread_id', 'html')
        sql = '''
            (SELECT board_post.thread_id, board_post.html
            FROM board_post
            WHERE board_post.thread_id = {thread_id}
            AND board_post.is_op_post = 1
            AND board_post.is_deleted = 0)
            UNION ALL
            (SELECT board_post.thread_id, board_post.html
            FROM board_post
            WHERE board_post.thread_id = {thread_id}
            AND board_post.is_deleted = 0
            ORDER BY board_post.id ASC
            LIMIT {offset}, {limit})
        '''.format(thread_id=self.id, offset=offset, limit=limit)
        cursor = connection.cursor()
        cursor.execute(sql)

        return (dict(zip(fields, i)) for i in cursor.fetchall())

    def last_posts(self):
        c = self.count()
        s = self.posts()
        all = s.all()
        if not c['skipped']:
            return all
        else:  # select first one and last 5 posts
            start, stop = c['start'], c['stop']
            return [all[0]] + list(all[start:stop])

    def remove(self):
        """Deletes thread."""
        self.posts().update(is_deleted=True)
        self.is_deleted = True
        self.save(rebuild_cache=False)

    def rebuild_cache(self, with_op_post=False):
        """Regenerates cache of OP-post and last 5."""
        if with_op_post:
            self.op_post.save(rebuild_cache=False)
        self.html = render_to_string('thread.html', {'thread': self})
        if with_op_post:
            self.op_post.save(rebuild_cache=True)

    def save(self, rebuild_cache=True):
        """Saves thread and rebuilds cache."""
        if rebuild_cache:
            super(Thread, self).save()
            self.rebuild_cache()
        super(Thread, self).save()
        # remove first thread in section
        ts = self.section.thread_set.filter(is_pinned=False)
        if ts.count() > self.section.threadlimit:
            ts.order_by('bump')[0].delete()

    def __unicode__(self):
        return unicode(self.op_post)

    class Meta:
        verbose_name = _('Thread')
        verbose_name_plural = _('Threads')
        get_latest_by = 'bump'
        ordering = ['-bump']


class Post(models.Model):
    """Represents post."""
    pid = models.PositiveIntegerField(blank=True, db_index=True,
        verbose_name=_('PID'))
    thread = models.ForeignKey('Thread', blank=True, null=True,
        verbose_name=_('Thread'))
    is_op_post = models.BooleanField(default=False,
        verbose_name=_('First post in thread'))
    date = models.DateTimeField(default=datetime.now, blank=True,
        verbose_name=_('Bump date'))
    is_deleted = models.BooleanField(default=False,
        verbose_name=_('Is deleted'))
    file_count = models.SmallIntegerField(default=0,
        verbose_name=_('File count'), blank=True)
    ip = models.IPAddressField(verbose_name=_('IP'), blank=True)
    data = fields.JSONField(max_length=1024, blank=True, null=True,
        verbose_name=_('Data'))
    #country = models.CharField(max_length=5, blank=True,
    #    verbose_name=_('Country code'))  # used for /int/-like sections
    poster = models.CharField(max_length=32, blank=True, null=True,
        verbose_name=_('Poster'))
    tripcode = models.CharField(max_length=32, blank=True,
        verbose_name=_('Tripcode'))
    email = models.CharField(max_length=32, blank=True,
        verbose_name=_('Email'))
    topic = models.CharField(max_length=48, blank=True,
        verbose_name=_('Topic'))
    password = models.CharField(max_length=64, blank=False,
        verbose_name=_('Password'))
    message = models.TextField(blank=True, verbose_name=_('Message'))
    html = models.TextField(blank=True, verbose_name=_('HTML cache'))
    objects = PostManager()
    deleted_objects = DeletedPostManager()

    allowed_fields = (
        'id', 'pid', 'poster', 'tripcode', 'topic', 'is_op_post',
        'date', 'message', 'email', 'data',
        ('thread', ('id', ('section', ('id', 'slug')))),
        'files',
    )

    def section(self):
        return self.thread.section

    def section_slug(self):
        return self.thread.section.slug

    def files(self):
        """Workaround for REST api."""
        return self.file_set.filter(is_deleted=False)

    def remove(self):
        """Visually deletes post."""
        if self.is_op_post:
            self.thread.remove()
        else:
            self.is_deleted = True
            self.save(rebuild_cache=False)
            self.thread.save(rebuild_cache=True)

    def rebuild_cache(self):
        """Regenerates html cache of post."""
        self.html = render_to_string('post.html', {'post': self})

    def save(self, rebuild_cache=True):
        if rebuild_cache:
            if not self.id:
                super(Post, self).save()
            self.rebuild_cache()
        super(Post, self).save()

    def delete(self):
        super(Post, self).delete()
        if self.is_op_post:
            self.thread.delete()
        self.file_set.delete()

    def __unicode__(self):
        return '{0}/{1}'.format(self.thread.section.slug, self.pid)

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        get_latest_by = 'pid'
        ordering = ['pid']


class File(models.Model):
    """Represents files at the board."""
    post = models.ForeignKey('Post', verbose_name=_('Post'))
    name = models.CharField(max_length=64,
        verbose_name=_('Original name'))
    type = models.ForeignKey('FileType', verbose_name=_('Type'))
    size = models.PositiveIntegerField(verbose_name=_('Size'))
    is_deleted = models.BooleanField(default=False,
        verbose_name=_('Is deleted'))
    image_width = models.PositiveSmallIntegerField(blank=True,
        verbose_name=_('Image width'))
    image_height = models.PositiveSmallIntegerField(blank=True,
        verbose_name=_('Image height'))
    hash = models.CharField(max_length=32, blank=True,
        verbose_name=_('Hash'))
    file = models.FileField(upload_to=get_file_path('section'),
        verbose_name=_('Location'))
    thumb = models.ImageField(upload_to=get_file_path('thumbs'),
        verbose_name=_('Thumbnail'))
    objects = FileManager()
    deleted_objects = DeletedFileManager()

    allowed_fields = ('id', 'post', 'name', 'type', 'size',
        'image_width', 'image_height', 'hash', 'file', 'thumb')

    def remove(self):
        """Visually deletes file."""
        self.is_deleted = True
        self.save()
        self.post.save()
        self.post.thread.save()

    def __unicode__(self):
        return '{0}/{1}'.format(self.post.section_slug(), self.post.pid)

    class Meta:
        verbose_name = _('File')
        verbose_name_plural = _('Files')


class FileType(models.Model):
    """File type"""
    extension = models.CharField(max_length=10,
        verbose_name=_('Extension'))
    mime = models.CharField(max_length=250, blank=False,
        verbose_name=_('MIME'))
    group = models.ForeignKey('FileTypeGroup',
        verbose_name=_('Group'))

    allowed_fields = ('id', 'category_id', 'type', 'extension')

    def __unicode__(self):
        return self.extension

    class Meta:
        verbose_name = _('File type')
        verbose_name_plural = _('File types')


class FileTypeGroup(models.Model):
    """Category of files"""
    name = models.CharField(max_length=32,
        verbose_name=_('Name'))
    default_image = models.ImageField(upload_to='default/')

    allowed_fields = ('id', 'name')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('File type group')
        verbose_name_plural = _('File type group')


class Section(models.Model):
    """Board section."""
    slug = models.SlugField(max_length=5, unique=True,
        verbose_name=_('Slug'))
    name = models.CharField(max_length=64,
        verbose_name=_('Name'))
    description = models.TextField(blank=True,
        verbose_name=_('Description'))
    type = models.PositiveSmallIntegerField(default=1, choices=SECTION_TYPES,
        verbose_name=_('Type'))
    group = models.ForeignKey('SectionGroup',
        verbose_name=_('Group'))
    force_files = models.BooleanField(default=True,
        verbose_name=_('Force to post file on thread creation'))
    filesize_limit = models.PositiveIntegerField(default=MEGABYTE * 5,
        verbose_name=_('Filesize limit'))
    anonymity = models.BooleanField(default=False,
        verbose_name=_('Force anonymity'))
    default_name = models.CharField(max_length=64, default=_('Anonymous'),
        verbose_name=_('Default poster name'))
    filetypes = models.ManyToManyField('FileTypeGroup', blank=True,
        verbose_name=_('File types'))
    bumplimit = models.PositiveSmallIntegerField(default=500,
        verbose_name=_('Max posts in thread'))
    threadlimit = models.PositiveSmallIntegerField(default=200,
        verbose_name=_('Max threads'))
    objects = SectionManager()

    ONPAGE = 20
    allowed_fields = (
        'id', 'last_post_pid', 'bumplimit', 'description',
        'filesize_limit', 'default_name', 'anonymity', 'threadlimit',
        'group_id', 'type', 'slug', 'name'
    )

    def threads(self):
        return Thread.objects.filter(section=self.id).order_by(
            '-is_pinned', '-bump', '-id')

    def op_posts(self):
        """List of first posts in section."""
        return Post.objects.filter(is_op_post=True,
            thread__section=self.id).order_by('-date', '-pid')

    def posts(self):
        """List of posts in section."""
        return Post.objects.filter(thread__section=self.id).order_by(
            '-date', '-pid')

    def posts_html(self):
        return self.posts().values('html')

    def files(self):
        """List of files in section."""
        return File.objects.filter(post__thread__section=self.id)

    def allowed_filetypes(self):
        """List of allowed MIME types of section."""
        return dict(FileType.objects.filter(
            group__in=self.filetypes.all()).values('mime', 'extension'))

    @property
    def key(self):
        """Section last post PID cache key name."""
        return 'section_last_{slug}'.format(slug=self.slug)

    @property
    def pid(self):
        """Gets section last post PID."""
        return cache.get(self.key) or self.rebuild_cache()

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
            self.rebuild_cache()
        return cache.incr(self.key)

    def rebuild_cache(self):
        """Refreshes cache of section last post PID."""
        try:
            pid = Post.objects.filter(thread__section=self.id).latest().pid
        except Post.DoesNotExist:  # no posts in section
            pid = 0
        self.pid = pid
        return pid

    def save(self):
        super(Section, self).save()
        cache.delete('sections')
        template.rebuild_cache()

    def __unicode__(self):
        return self.slug

    class Meta:
        verbose_name = _('Section')
        verbose_name_plural = _('Sections')


class SectionGroup(models.Model):
    """Group of board sections. Example: [b / d / s] [a / aa]."""
    name = models.CharField(max_length=64, blank=False,
        verbose_name=_('Name'))
    order = models.SmallIntegerField(verbose_name=_('Order'))
    is_hidden = models.BooleanField(default=False, verbose_name=_('Is hidden'))
    objects = SectionGroupManager()
    allowed_fields = ('id', 'name', 'order', 'is_hidden')

    def save(self):
        super(SectionGroup, self).save()
        cache.delete('sections')
        template.rebuild_cache()

    def __unicode__(self):
        return unicode(self.name) + ', ' + unicode(self.order)

    class Meta:
        verbose_name = _('Section group')
        verbose_name_plural = _('Section groups')


class UserProfile(models.Model):
    """User (moderator etc.)."""
    user = models.ForeignKey(User)
    sections = models.ManyToManyField('Section', blank=False,
        verbose_name=_('User owned sections'))

    def modded(self):
        """List of modded section slugs."""
        return tools.take_first(self.sections.values_list('slug'))

    def moderates(self, section_slug):
        """Boolean value of user moderation rights of section_slug."""
        return self.user.is_superuser or section_slug in self.modded()

    def __unicode__(self):
        return '{0}'.format(self.user)

    class Meta:
        verbose_name = _('User profile')
        verbose_name_plural = _('User profiles')


class Wordfilter(models.Model):
    """Black list word, phrase."""
    word = models.CharField(max_length=100, unique=True,
        verbose_name=_('Word'))
    objects = WordfilterManager()

    def __unicode__(self):
        return self.word

    class Meta:
        verbose_name = _('Wordfilter')
        verbose_name_plural = _('Wordfilters')


class DeniedIP(models.Model):
    """Used for bans."""
    ip = models.CharField(_('IP network'), max_length=18, db_index=True,
            help_text=_('Either IP address or IP network specification'))
    reason = models.CharField(_('Ban reason'), max_length=128, db_index=True)
    by = models.ForeignKey(User)
    date = models.DateTimeField(default=datetime.now)

    def network(self):
        return Network(self.ip)

    def __unicode__(self):
        return '{0} @ {1}'.format(self.ip, self.date)

    class Meta:
        verbose_name = _('Denied IP')
        verbose_name_plural = _('Denied IPs')


class PostFormNoCaptcha(ModelForm):
    """Post form with no captcha.

       Used for disabling double requests to api server.
    """
    file = FileField(required=False)
    section = CharField(required=False)

    class Meta:
        model = Post


class PostForm(PostFormNoCaptcha):
    """Simple post form."""
    captcha = fields.ReCaptchaField(required=False)
    recaptcha_challenge_field = CharField(required=False)
    recaptcha_response_field = CharField(required=False)


class SectionFeed(Feed):
    """Section threads RSS feed. Contains last 40 items of section."""
    def get_object(self, request, section_slug):
        self.slug = section_slug
        return get_object_or_404(Section, slug=section_slug)

    def title(self, obj):
        return u'{title} - {last} {section}'.format(
            title=settings.SITE_TITLE, last=_('Last threads of section'),
            section=self.slug
        )

    def link(self, obj):
        return '/{0}/'.format(self.slug)

    def description(self, obj):
        return u'{last} {section}'.format(last=_('Last threads of section'),
            section=self.slug)

    def items(self):
        return Post.objects.filter(thread__section__slug=self.slug,
            is_op_post=True).reverse().values('pid', 'date', 'message')[:40]

    def item_title(self, item):
        return u'{0} {1}'.format(_('Thread'), item['pid'])

    def item_description(self, item):
        return item['message']

    def item_link(self, item):
        return '/{0}/{1}'.format(self.slug, item['pid'])


class ThreadFeed(Feed):
    """Thread posts RSS feed. Contains all posts in thread."""
    def get_object(self, request, section_slug, op_post):
        try:
            post = Post.objects.get(thread__section__slug=section_slug,
                pid=op_post, is_op_post=True)
        except Post.DoesNotExist:
            raise Http404
        t = post.thread
        self.slug = section_slug
        self.op_post = op_post
        self.posts = t.posts().reverse().values('pid', 'date', 'message')
        return t

    def title(self, obj):
        return u'{title} - {last} {section}/{op_post}'.format(
            title=settings.SITE_TITLE, last=_('Last posts of thread'),
            section=self.slug, op_post=self.op_post
        )

    def link(self, obj):
        return '/{0}/{1}'.format(self.slug, self.op_post)

    def description(self, obj):
        return u'{last} {op_post}'.format(last=_('Last posts of thread'),
            op_post=self.op_post)

    def items(self):
        return self.posts

    def item_title(self, item):
        return u'{0} {1}'.format(_('Post'), item['pid'])

    def item_description(self, item):
        return item['message']

    def item_link(self, item):
        return '/{0}/{1}#{2}'.format(self.slug, self.op_post, item['pid'])


def create_user_profile(sender, instance, created, **kwargs):
    """Connects UserProfile class with builtit User."""
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)

models.signals.post_save.connect(create_user_profile, sender=User)
