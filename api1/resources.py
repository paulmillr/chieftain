from djangorestframework.resources import ModelResource

from board import models


class ThreadResource(ModelResource):
    """A read/delete resource for Thread."""
    model = models.Thread
    fields = (
        "id", "section_id", "bump", "is_pinned",
        "is_closed", "html",
    )


class PostResource(ModelResource):
    """A create/list resource for Post."""
    form = models.PostFormNoCaptcha
    model = models.Post
    fields = [
        "id", "pid", "poster", "tripcode", "topic", "is_op_post",
        "date", "message", "email", "data", "file",
        ("thread", ("id", ("section", ("id", "slug")))),
    ]


class SectionResource(ModelResource):
    """A read resource for Section."""
    model = models.Section
    fields = (
        "id", "last_post_pid", "bumplimit", "description",
        "filesize_limit", "default_name", "anonymity", "threadlimit",
        "group_id", "type", "slug", "name"
    )


class SectionGroupResource(ModelResource):
    """A read resource for SectionGroup."""
    model = models.SectionGroup
    fields = ("id", "name", "order", "is_hidden")


class FileResource(ModelResource):
    """A list resource for File."""
    model = models.File
    fields = ("id", "post", "name", "type", "size", "image_width",
              "image_height", "hash", "file", "thumb")


class FileTypeResource(ModelResource):
    """A read resource for FileType."""
    model = models.FileType
    fields = ("id", "category_id", "type", "extension")


class FileTypeGroupResource(ModelResource):
    """A read resource for FileTypeGroup."""
    model = models.FileTypeGroup
