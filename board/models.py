# coding: utf-8
from django.db import models, connection
from django.db.models.query import QuerySet
from denorm import CountField

class Thread(models.Model):
    """Represents topic"""
    # op_post = models.ForeignKey('Post', related_name='-')
    #posts = CountField('post_set')
    bump = models.DateTimeField(blank=True)
    is_pinned = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    def posts(self):
        return Post.objects.filter(thread=self.id)
    def last_posts(self):
        lp = 5
        ps = self.post_set
        stop = ps.count()
        all = ps.all()
        if stop <= lp: # if we got thread with less posts than lp
            return all
        else:
            start = stop - lp
            return [all[0]] + list(all[start:stop]) # select last 5 posts
        
    def __unicode__(self):
        return unicode(self.id)

class Post(models.Model):
    """Represents post"""
    section = models.ForeignKey('Section')
    pid = models.PositiveIntegerField()
    thread = models.ForeignKey('Thread', blank=True)
    is_op_post = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(blank=True)
    ip = models.IPAddressField()
    poster = models.CharField(max_length=32, blank=True)
    tripcode = models.CharField(max_length=32, blank=True)
    email = models.CharField(max_length=32, blank=True)
    topic = models.CharField(max_length=48, blank=True)
    password = models.CharField(max_length=32, blank=True)
    message = models.TextField(blank=True)
    def __unicode__(self):
        return self.section.slug+'/'+unicode(self.id)

class File(models.Model):
    """Represents files at the board"""
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
    slug = models.SlugField(max_length=5)
    name = models.CharField(max_length=64)
    description = models.TextField(blank=False)
    group = models.ForeignKey('SectionGroup')
    filesize_limit = models.PositiveIntegerField(default=5*2**20) # 5mb
    anonymity = models.BooleanField(default=False)
    default_name = models.CharField(max_length=64, default='Anonymous')
    filetypes = models.ManyToManyField(FileCategory)
    bumplimit = models.PositiveSmallIntegerField(default=500)
    threadlimit = models.PositiveSmallIntegerField(default=10)
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