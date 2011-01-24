# coding: utf-8
from django.db import models, connection
from django.db.models.query import QuerySet
from django.core.paginator import Paginator
from django.core.cache import cache
from django.forms import ModelForm
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from hashlib import sha1

DAY = 86400 # seconds in day

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

class PostManager(models.Manager):
    @cached(3 * DAY)
    def thread_id(self, slug, op_post):
        """Gets thread id by slug and op_post pid."""
        try:
            t = self.get(thread__section__slug=slug, pid=op_post, 
                is_op_post=True).thread.id
        except (Post.DoesNotExist), e:
            raise e
        else:
            return t

class SectionManager(models.Manager):
    @cached(DAY)
    def sections(self):
        """Gets list of board sections.

           We're not using QuerySet because they cannot be cached.
        """
        return Section.objects.all().order_by('slug')

class SectionGroupManager(models.Manager):
    """docstring for SectionGroupManager"""
    @cached(DAY)
    def sections(self):
        """Gets list of board sections.

           We're not using QuerySet because they cannot be cached.
        """
        groups = SectionGroup.objects.all().order_by('order')
        data = [] # http://goo.gl/CpPq6
        for group in groups:
            d = {
                'id' : group.id,
                'name' : group.name, 
                'order' : group.order, 
                'is_hidden' : group.is_hidden,
                'sections' : list(group.section_set.values())
            }
            data.append(d)
        return data
        

class Thread(models.Model):
    """Groups of posts."""
    section = models.ForeignKey('Section')
    bump = models.DateTimeField(blank=True, verbose_name=_('Thread bump date'))
    is_pinned = models.BooleanField(default=False, 
        verbose_name=_('Thread is pinned'))
    is_closed = models.BooleanField(default=False, 
        verbose_name=_('Thread is closed'))
    html = models.TextField(blank=True, verbose_name=_('Thread html'))
    def posts_html(self):
        return self.post_set.values('html')
        
    def postcount(self):
        return self.post_set.count()
        
    def count(self):
        lp = 5
        ps = self.post_set
        stop = ps.count()
        if stop <= lp: # if we got thread with less posts than lp
            return {'total' : stop, 'skipped' : 0, 'skipped_files' : 0}
        else:
            start = stop - lp
            return {
                'total' : stop, 'start' : start, 'stop' : stop,
                'skipped' : start - 1, 
                'skipped_files' : ps.filter(file_count__gt=0).count()
            }
    
    def op_post(self):
        return self.post_set.all()[0]
        
    def last_posts(self):
        c = self.count()
        s = self.post_set
        all = s.all()
        if c['skipped'] == 0:
            return all
        else: # select first one and last 5 posts
            start, stop = c['start'], c['stop']
            return [s.all()[0]] + list(all[start:stop])
    
    def refresh_cache(self):
        """Regenerates cache of OP-post and last 5."""
        self.html = render_to_string('section_thread.html', {'thread' : self})
        self.save()
    
    def __unicode__(self):
        return unicode(self.id)

class Post(models.Model):
    """Represents post."""
    pid = models.PositiveIntegerField(blank=True)
    thread = models.ForeignKey('Thread', blank=True, 
        verbose_name=_('Post thread'))
    is_op_post = models.BooleanField(default=False, 
        verbose_name=_('Post is op post'))
    date = models.DateTimeField(auto_now_add=True, verbose_name=_('Post bump date'))
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
    password = models.CharField(max_length=32, blank=True,
        verbose_name=_('Post password'))
    message = models.TextField(verbose_name=_('Post message'))
    html = models.TextField(blank=True, verbose_name=_('Post html'))
    objects = PostManager()
    def refresh_cache(self):
        """Regenerates html cache of post."""
        self.html = render_to_string('post.html', {'post' : self})
        self.save()
        
    def __unicode__(self):
        return unicode(self.id)

class File(models.Model):
    """Represents files at the board."""
    post = models.ForeignKey('Post', verbose_name=_('File post'))
    name = models.CharField(max_length=64, 
        verbose_name=_('File original name')) # original file name
    mime = models.ForeignKey('FileType', verbose_name=_('File MIME'))
    size = models.PositiveIntegerField(verbose_name=_('file_size'))
    is_deleted = models.BooleanField(blank=False, 
        verbose_name=_('File is deleted'))
    image_width = models.PositiveSmallIntegerField(blank=False,
        verbose_name=_('File image width'))
    image_height = models.PositiveSmallIntegerField(blank=False,
        verbose_name=_('File image height'))
    #meta = models.TextField()
    hash = models.CharField(max_length=32, blank=False,
        verbose_name=_('File hash'))
    file = models.FileField(upload_to=lambda *x: \
        '{.board}/{.thread}/{.pid}.{.mime.extension}'.format(*x),
        verbose_name=_('File location'))

class FileCategory(models.Model):
    """Category of files"""
    name = models.CharField(max_length=32, verbose_name=_('File category name'))
    def __unicode__(self):
        return self.name

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

class Section(models.Model):
    """Board section"""
    slug = models.SlugField(max_length=5, unique=True, 
        verbose_name=_('Section slug'))
    name = models.CharField(max_length=64,
        verbose_name=_('Section name'))
    description = models.TextField(blank=False,
        verbose_name=_('Section description'))
    group = models.ForeignKey('SectionGroup',
        verbose_name=_('Section group'))
    filesize_limit = models.PositiveIntegerField(default=5*2**20, # 5mb
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
        threads = Paginator(self.thread_set.all(), onpage)
        return threads.page(page)
    
    def get_cache_key(self):
        return 'section_last_{slug}'.format(slug=self.slug)
    
    def last_post_pid(self):
        """
           Gets last post pid. Pid is unique to section. 
           This method is cached.
        """
        d = cache.get(self.get_cache_key())
        if d is not None:
            return d
        return self.refresh_cache()
    
    def refresh_cache(self):
        """Refreshes cache of section-last_post_pid."""
        p = Post.objects.filter(thread__section=self.id)
        pid = p[p.count()-1].pid # get last post
        cache.set(self.get_cache_key(), pid)
        return pid
        
    def __unicode__(self):
        return self.slug

class SectionGroup(models.Model):
    """Group of board sections. Example: [b / d / s] [a / aa] """
    name = models.CharField(max_length=64, blank=False,
        verbose_name=_('Section group name'))
    order = models.SmallIntegerField(verbose_name=_('Section group order'))
    objects = SectionGroupManager()
    # determine if section hidden from menu or not
    is_hidden = models.BooleanField(default=False)
    def __unicode__(self):
        return unicode(self.name) + ', ' + unicode(self.order)

class User(models.Model):
    """User (moderator etc.)"""
    username = models.CharField(max_length=32, unique=True,
        verbose_name=_('User name'))
    password = models.CharField(max_length=32,
        verbose_name=_('User password'))
    # sections, modded by user
    sections = models.ManyToManyField('Section', blank=False,
        verbose_name=_('User owned sections'))
    def __unicode__(self):
        return self.username

class PostForm(ModelForm):
    class Meta:
        model = Post