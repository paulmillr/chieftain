# coding: utf-8
from django.db import models, connection
from django.db.models.query import QuerySet
from django.core.paginator import Paginator
from django.core.cache import cache
from hashlib import sha1

def cached(seconds = 900):
    """
        Cache the result of a function call for the specified number of seconds, 
        using Django's caching mechanism.
    """
    def doCache(f):
        def x(*args, **kwargs):
                key = sha1(str(f.__module__) + str(f.__name__) + str(args) + str(kwargs)).hexdigest()
                result = cache.get(key)
                if result is None:
                    result = f(*args, **kwargs)
                    cache.set(key, result, seconds)
                return result
        return x
    return doCache

class SectionManager(models.Manager):
    """Section methods"""
    def by_slug(self, slug):
        return self.get(slug__iexact=slug)

class Thread(models.Model):
    """Groups of posts."""
    section = models.ForeignKey('Section')
    bump = models.DateTimeField(blank=True)
    is_pinned = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    page_html = models.TextField(blank=True)
    def posts(self):
        return self.post_set.filter(thread=self.id)
    def postcount(self):
        return self.posts.count()
    def count(self):
        lp = 5
        ps = self.post_set
        stop = ps.count()
        if stop <= lp: # if we got thread with less posts than lp
            return {'total' : stop, 'skipped' : 0, 'skipped_files' : 0}
        else:
            start = stop - lp
            return {'total' : stop, 'start' : start, 'stop' : stop,
                'skipped' : start - 1, 'skipped_files' : ps.filter(file_count__gt=0).count()}
    def last_posts(self):
        c = self.count()
        s = self.post_set
        all = s.all()
        if c['skipped'] == 0:
            return all
        else:
            start, stop = c['start'], c['stop']
            return [s.all()[0]] + list(all[start:stop]) # select last 5 posts
        
    def __unicode__(self):
        return unicode(self.id)

class Post(models.Model):
    """Represents post."""
    pid = models.PositiveIntegerField()
    thread = models.ForeignKey('Thread', blank=True)
    is_op_post = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    file_count = models.SmallIntegerField(default=0)
    ip = models.IPAddressField()
    poster = models.CharField(max_length=32, blank=True)
    tripcode = models.CharField(max_length=32, blank=True)
    email = models.CharField(max_length=32, blank=True)
    topic = models.CharField(max_length=48, blank=True)
    password = models.CharField(max_length=32, blank=True)
    message = models.TextField(blank=True)
    html = models.TextField(blank=True)
    def __unicode__(self):
        return unicode(self.id)

class File(models.Model):
    """Represents files at the board."""
    post = models.ForeignKey('Post')
    name = models.CharField(max_length=64) # original file name
    mime = models.ForeignKey('FileType')
    size = models.PositiveIntegerField()
    is_deleted = models.BooleanField(blank=False)
    image_width = models.PositiveSmallIntegerField(blank=False)
    image_height = models.PositiveSmallIntegerField(blank=False)
    #meta = models.TextField()
    hash = models.CharField(max_length=32, blank=False)
    file = models.FileField(upload_to=lambda *x: \
        '{.board}/{.thread}/{.pid}.{.mime.extension}'.format(*x))

class FileCategory(models.Model):
    """Category of files"""
    name = models.CharField(max_length=32)
    def __unicode__(self):
        return self.name

class FileType(models.Model):
    """File type"""
    extension = models.CharField(max_length=10, unique=True)
    mime = models.CharField(max_length=250, blank=False)
    category = models.ForeignKey('FileCategory')
    def __unicode__(self):
        return self.extension

class Section(models.Model):
    """Board section"""
    slug = models.SlugField(max_length=5, unique=True)
    name = models.CharField(max_length=64)
    description = models.TextField(blank=False)
    group = models.ForeignKey('SectionGroup')
    filesize_limit = models.PositiveIntegerField(default=5*2**20) # 5mb
    anonymity = models.BooleanField(default=False)
    default_name = models.CharField(max_length=64, default='Anonymous')
    filetypes = models.ManyToManyField(FileCategory)
    bumplimit = models.PositiveSmallIntegerField(default=500)
    threadlimit = models.PositiveSmallIntegerField(default=10)
    objects = SectionManager()
    def threads(self):
        return self.thread_set.filter(section=self.id)
    def page_threads(self, page=1):
        onpage = 20
        threads = Paginator(Thread.objects.filter(section=self.id), onpage)
        return threads.page(page)
    def __unicode__(self):
        return self.slug

class SectionGroup(models.Model):
    """Group of board sections. Example: [b / d / s] [a / aa] """
    name = models.CharField(max_length=64, blank=False)
    order = models.SmallIntegerField()
    def sections(self):
        return self.section_set.values()
    # determine if section hidden from menu or not
    is_hidden = models.BooleanField(default=False)
    def __unicode__(self):
        return unicode(self.name) + ', ' + unicode(self.order)

class User(models.Model):
    """User (moderator etc.)"""
    username = models.CharField(max_length=32, unique=True)
    password = models.CharField(max_length=32)
    # sections, modded by user
    sections = models.ManyToManyField('Section', blank=False)
    def __unicode__(self):
        return self.username