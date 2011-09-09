# encoding: utf-8
from random import randint
from hashlib import sha1
from datetime import datetime

from ipcalc import Network
from dmark import DMark

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.syndication.views import Feed
from django.core.cache import cache
from django.db import models
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from board import fields, tools

__all__ = [
    "cached",
    "Post", "Thread", "Section", "SectionGroup",
    "File", "FileType", "FileTypeGroup",
    "PostManager", "SectionManager", "SectionGroupManager",
    "UserProfile",
    "PostFormNoCaptcha", "PostForm", "Wordfilter", "DeniedIP",
    "SectionFeed", "ThreadFeed",
]


def get_file_path(base):
    """Builds path to stored static files. Used in File class."""
    def closure(instance, filename):
        return "{base}/{timestamp}{salt}.{ext}".format(
            base=base, timestamp=tools.timestamp_now(),
            salt=randint(10, 99), ext=instance.type.extension
        )
    return closure


def cached(seconds=15 * 60, key=None):
    """Cache the result of a function call."""
    def do_cache(f):
        def closure(*args, **kwargs):
            cache_key = key or sha1(f.__module__ + f.__name__ +
                                    str(args) + str(kwargs)).hexdigest()

            result = cache.get(cache_key)
            if result is None:
                result = f(*args, **kwargs)
                cache.set(cache_key, result, seconds)
            return result
        return closure
    return do_cache


class _DeletionMixIn(object):
    def get_query_set(self):
        return super(_DeletionMixIn, self).get_query_set() \
               .filter(is_deleted=("Deleted" in self.__class__.__name__))


class ThreadManager(_DeletionMixIn, models.Manager):
    pass


class DeletedThreadManager(ThreadManager):
    pass


class PostManager(_DeletionMixIn, models.Manager):
    pass


class DeletedPostManager(PostManager):
    pass


class FileManager(_DeletionMixIn, models.Manager):
    def random_images(self):
        return self.filter(image_width__gt=200).order_by("?")


class DeletedFileManager(FileManager):
    pass


class SectionManager(models.Manager):
    pass


class SectionGroupManager(models.Manager):
    """Manager for SectionGroup."""
    @cached(24 * 60 * 60, "sections")
    def tree(self):
        """
           Gets list of board sections.
           We're not using QuerySet because they cannot be cached.
        """
        data = []
        sections = list(Section.objects.all().values())
        for g in self.order_by("order").values():
            g["sections"] = [s for s in sections if s["group_id"] == g["id"]]
            data.append(g)
        return data


class WordfilterManager(models.Manager):
    """Manager for Wordfilter."""

    def words(self):
        return tools.take_first(self.values_list("word"))

    def scan(self, message):
        return any(word in message for word in self.words())


class Thread(models.Model):
    """Groups of posts."""
    section = models.ForeignKey("Section")
    bump = models.DateTimeField(_("Bump date"), blank=True, db_index=True)
    is_pinned = models.BooleanField(_("Is pinned"), default=False)
    is_closed = models.BooleanField(_("Is closed"), default=False)
    is_deleted = models.BooleanField(_("Is deleted"), default=False)
    # basically, this needs to be stored in some sort of cache
    # but because of star location, we'll use sql.
    # sorry for the denormalization
    html = models.TextField(blank=True)
    objects = ThreadManager()
    deleted_objects = DeletedThreadManager()

    class Meta:
        verbose_name = _("Thread")
        verbose_name_plural = _("Threads")
        get_latest_by = "bump"
        ordering = ["-bump"]

    def __unicode__(self):
        return unicode(self.op_post)

    def save(self, rebuild_cache=True):
        """Saves thread and rebuilds cache."""
        if rebuild_cache:
            super(Thread, self).save()
            self.rebuild_cache()
        super(Thread, self).save()
        # remove first thread in section
        ts = self.section.thread_set.filter(is_pinned=False)
        if ts.count() > self.section.threadlimit:
            ts.order_by("bump")[0].delete()

    def posts(self):
        """Returns thread posts."""
        return self.post_set.all()

    def posts_html(self):
        return self.posts().values("html", "ip")

    def count(self, limit=5):
        """Returns dict, that contains info about thread files and posts."""
        ps = self.posts()
        total = ps.count()
        if total <= limit:
            return {"total": total, "skipped": 0, "skipped_files": 0}
        start = total - limit
        skipped_ids = tools.take_first(ps[1:start].values_list("id"))
        return {
            "total": total,
            "start": start,
            "stop": total,
            "skipped": start - 1,
            "skipped_files": ps.filter(id__in=skipped_ids, file=True).count()
        }

    @property
    def op_post(self):
        if not self.is_deleted:
            post_set = self.post_set
        else:
            post_set = Post.deleted_objects.filter(thread=self)
        return post_set.filter(is_op_post=True).get()

    def last_posts(self):
        c = self.count()
        s = self.posts()
        posts = s.all()
        if not c["skipped"]:
            return posts
        # select first and last 5 posts
        start, stop = c["start"], c["stop"]
        return [posts[0]] + list(posts[start:stop])

    def remove(self):
        """Deletes thread."""
        self.posts().update(is_deleted=True)
        self.is_deleted = True
        self.save(rebuild_cache=False)

    def rebuild_cache(self, with_op_post=False):
        """Regenerates cache of OP-post and last 5."""
        if with_op_post:
            self.op_post.save(rebuild_cache=False)
        self.html = render_to_string("thread.html", {"thread": self})
        if with_op_post:
            self.op_post.save(rebuild_cache=True)


class Post(models.Model):
    """Represents post."""
    pid = models.PositiveIntegerField(_("PID"), blank=True, db_index=True)
    thread = models.ForeignKey("Thread", verbose_name=_("Thread"), blank=True,
        null=True)
    is_op_post = models.BooleanField(_("First post in thread"), default=False)
    date = models.DateTimeField(_("Bump date"), default=datetime.now,
        blank=True)
    is_deleted = models.BooleanField(_("Is deleted"), default=False)
    ip = models.IPAddressField(_("IP"), blank=True)
    data = fields.JSONField(_("Data"), max_length=1024, blank=True, null=True)
    poster = models.CharField(_("Poster"), max_length=32, blank=True,
        null=True)
    tripcode = models.CharField(_("Tripcode"), max_length=32, blank=True)
    email = models.CharField(_("Email"), max_length=32, blank=True)
    topic = models.CharField(_("Topic"), max_length=48, blank=True)
    file = models.OneToOneField("File", verbose_name=_("File"), blank=True,
        null=True)
    password = models.CharField(_("Password"), max_length=64, blank=True)
    message = models.TextField(_("Message"), blank=True)
    message_html = models.TextField(blank=True)
    html = models.TextField(blank=True)  # again, sort of cache
    objects = PostManager()
    deleted_objects = DeletedPostManager()

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        get_latest_by = "pid"
        ordering = ["pid"]

    def __unicode__(self):
        return "{}/{}".format(self.thread.section.slug, self.pid)

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

    def section(self):
        return self.thread.section

    def section_slug(self):
        return self.thread.section.slug

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
        self.message_html = DMark().convert(self.message).encode("utf-8")
        self.html = render_to_string("post.html", {"post": self})


class File(models.Model):
    """Represents files at the board."""
    name = models.CharField(_("Original name"), max_length=64)
    type = models.ForeignKey("FileType", verbose_name=_("Type"))
    is_deleted = models.BooleanField(_("Is deleted"), default=False)
    hash = models.CharField(_("Hash"), max_length=32, blank=True)
    file = models.FileField(_("Location"), upload_to=get_file_path("section"))
    thumb = models.ImageField(_("Thumbnail"),
        upload_to=get_file_path("thumbs"))
    image_width = models.PositiveSmallIntegerField(_("Image width"),
        blank=True)
    image_height = models.PositiveSmallIntegerField(_("Image height"),
        blank=True)
    objects = FileManager()
    deleted_objects = DeletedFileManager()

    class Meta:
        verbose_name = _("File")
        verbose_name_plural = _("Files")

    def __unicode__(self):
        return "{}/{}".format(self.post.section_slug(), self.post.pid)

    @property
    def post(self):
        return self.post_set.get()

    def remove(self):
        """Visually deletes file."""
        self.is_deleted = True
        self.save()
        self.post.save()
        self.post.thread.save()


class FileType(models.Model):
    """File type"""
    extension = models.CharField(_("Extension"), max_length=10)
    mime = models.CharField(_("MIME"), max_length=250)
    group = models.ForeignKey("FileTypeGroup", verbose_name=_("Group"))

    class Meta:
        verbose_name = _("File type")
        verbose_name_plural = _("File types")

    def __unicode__(self):
        return self.extension


class FileTypeGroup(models.Model):
    """Category of files"""
    name = models.CharField(_("Name"), max_length=32)
    default_image = models.ImageField(upload_to="default/")

    class Meta:
        verbose_name = _("File type group")
        verbose_name_plural = _("File type group")

    def __unicode__(self):
        return self.name


class Section(models.Model):
    """Board section."""
    SECTION_TYPES = (
        (1, _("Default")),
        (2, _("Premodded")),
        (3, _("News")),
        (4, _("International")),
        (5, _("Software")),
        (6, _("Chat")),
    )

    slug = models.SlugField(_("Slug"), max_length=5, unique=True)
    name = models.CharField(_("Name"), max_length=64)
    description = models.TextField(_("Description"), blank=True)
    type = models.PositiveSmallIntegerField(_("Type"), default=1,
        choices=SECTION_TYPES)
    group = models.ForeignKey("SectionGroup", verbose_name=_("Group"))
    force_files = models.BooleanField(
        _("Force to post file on thread creation"), default=True)
    filesize_limit = models.PositiveIntegerField(_("Filesize limit"),
        default=2 ** 20 * 5)
    anonymity = models.BooleanField(_("Force anonymity"), default=False)
    default_name = models.CharField(_("Default poster name"), max_length=64,
        default=_("Anonymous"))
    filetypes = models.ManyToManyField("FileTypeGroup",
        verbose_name=_("File types"), blank=True)
    bumplimit = models.PositiveSmallIntegerField(_("Max posts in thread"),
        default=500)
    threadlimit = models.PositiveSmallIntegerField(_("Max threads"),
        default=200)
    objects = SectionManager()

    ONPAGE = 20

    class Meta:
        verbose_name = _("Section")
        verbose_name_plural = _("Sections")

    def __unicode__(self):
        return self.slug

    def save(self):
        super(Section, self).save()
        cache.delete("sections")

    def threads(self):
        return Thread.objects.filter(section=self.id).order_by(
            "-is_pinned", "-bump", "-id")

    def op_posts(self):
        """List of first posts in section."""
        return Post.objects.filter(is_op_post=True,
            thread__section=self.id).order_by("-date", "-pid")

    def posts(self):
        """List of posts in section."""
        return Post.objects.filter(thread__section=self.id).order_by(
            "-date", "-pid")

    def posts_html(self):
        return self.posts().values("html")

    def files(self):
        """List of files in section."""
        return File.objects.filter(post__thread__section=self.id)

    def allowed_filetypes(self):
        """List of allowed MIME types of section."""
        return dict(FileType.objects.filter(
            group__in=self.filetypes.all()).values_list("mime", "extension"))

    @property
    def key(self):
        """Section last post PID cache key name."""
        return "section_last_{slug}".format(slug=self.slug)

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


class SectionGroup(models.Model):
    """Group of board sections. Example: [b / d / s] [a / aa]."""
    name = models.CharField(_("Name"), max_length=64)
    order = models.SmallIntegerField(_("Order"))
    is_hidden = models.BooleanField(_("Is hidden"), default=False)
    objects = SectionGroupManager()

    class Meta:
        verbose_name = _("Section group")
        verbose_name_plural = _("Section groups")

    def __unicode__(self):
        return u"{}, {}".format(self.name, self.order)

    def save(self):
        super(SectionGroup, self).save()
        cache.delete("sections")


class UserProfile(models.Model):
    """User (moderator etc.)."""
    user = models.OneToOneField(User)
    sections = models.ManyToManyField("Section",
        verbose_name=_("User owned sections"))

    class Meta:
        verbose_name = _("User profile")
        verbose_name_plural = _("User profiles")

    def __unicode__(self):
        return self.user

    def modded(self):
        """List of modded section slugs."""
        return tools.take_first(self.sections.values_list("slug"))

    def moderates(self, section_slug):
        """Boolean value of user moderation rights of section_slug."""
        return self.user.is_superuser or section_slug in self.modded()


class Wordfilter(models.Model):
    """Black list word, phrase."""
    word = models.CharField(_("Word"), max_length=100, unique=True)
    objects = WordfilterManager()

    class Meta:
        verbose_name = _("Wordfilter")
        verbose_name_plural = _("Wordfilters")

    def __unicode__(self):
        return self.word


class DeniedIP(models.Model):
    """Used for bans."""
    ip = models.CharField(_("IP network"), max_length=18, db_index=True,
        help_text=_("Either IP address or IP network specification"))
    reason = models.CharField(_("Ban reason"), max_length=128, db_index=True)
    by = models.ForeignKey(User)
    date = models.DateTimeField(default=datetime.now)

    class Meta:
        verbose_name = _("Denied IP")
        verbose_name_plural = _("Denied IPs")

    def __unicode__(self):
        return "{} @ {}".format(self.ip, self.date)

    def network(self):
        return Network(self.ip)


class PostFormNoCaptcha(forms.ModelForm):
    """Post form with no captcha.

       Used for disabling double requests to api server.
    """
    section = forms.CharField(required=False)
    captcha = forms.CharField(required=False)
    recaptcha_challenge_field = forms.CharField(required=False)
    recaptcha_response_field = forms.CharField(required=False)

    class Meta:
        model = Post


class PostForm(PostFormNoCaptcha):
    """Simple post form."""
    captcha = fields.ReCaptchaField(required=False)


class SectionFeed(Feed):
    """Section threads RSS feed. Contains last 40 items of section."""
    def get_object(self, request, section_slug):
        self.slug = section_slug
        return get_object_or_404(Section, slug=section_slug)

    def title(self, obj):
        return u"{title} - {last} {section}".format(
            title=settings.SITE_TITLE, last=_("Last threads of section"),
            section=self.slug
        )

    def link(self, obj):
        return "/{}/".format(self.slug)

    def description(self, obj):
        return u"{last} {section}".format(last=_("Last threads of section"),
            section=self.slug)

    def items(self):
        return Post.objects.filter(thread__section__slug=self.slug,
            is_op_post=True).reverse().values("pid", "date", "message")[:40]

    def item_title(self, item):
        return u"{} {}".format(_("Thread"), item["pid"])

    def item_description(self, item):
        return item["message"]

    def item_link(self, item):
        return "/{}/{}".format(self.slug, item["pid"])


class ThreadFeed(Feed):
    """Thread posts RSS feed. Contains all posts in thread."""
    def get_object(self, request, section_slug, op_post):
        post = get_object_or_404(Post,
            thread__section__slug=section_slug,
            pid=op_post, is_op_post=True
        )
        t = post.thread
        self.slug = section_slug
        self.op_post = op_post
        self.posts = t.posts().reverse().values("pid", "date", "message")
        return t

    def title(self, obj):
        return u"{title} - {last} {section}/{op_post}".format(
            title=settings.SITE_TITLE, last=_("Last posts of thread"),
            section=self.slug, op_post=self.op_post
        )

    def link(self, obj):
        return "/{}/{}".format(self.slug, self.op_post)

    def description(self, obj):
        return u"{last} {op_post}".format(last=_("Last posts of thread"),
            op_post=self.op_post)

    def items(self):
        return self.posts

    def item_title(self, item):
        return u"{} {}".format(_("Post"), item["pid"])

    def item_description(self, item):
        return item["message"]

    def item_link(self, item):
        return "/{}/{}#{}".format(self.slug, self.op_post, item["pid"])


def create_user_profile(sender, instance, created, **kwargs):
    """Connects UserProfile class with builtit User."""
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)

models.signals.post_save.connect(create_user_profile, sender=User)
