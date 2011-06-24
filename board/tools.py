# encoding: utf-8
import os
import re
import httpagentparser
import string
import sys
from crypt import crypt
from datetime import datetime
from hashlib import sha1
from PIL import Image
from random import choice
from tempfile import NamedTemporaryFile
from time import time
from django.conf import settings
from django.core.files import File as DjangoFile


__all__ = [
    "handle_uploaded_file", "make_tripcode", "random_text",
    "get_key", "parse_user_agent", "make_post_descriptions",
    "take_first", "from_timestamp", "print_flush"
]


def handle_uploaded_file(file_instance):
    """Moves uploaded file to files directory and makes thumb."""
    def make_path(dir):
        return os.path.join(settings.MEDIA_ROOT, dir)
    f = file_instance
    directory = make_path("section")
    if not os.path.isdir(directory):
        os.makedirs(directory)
    f.save()
    try:  # make thumb
        img = Image.open(f.file.file)
        f.image_height, f.image_width = img.size
        MAX = 200
        if max(img.size) < MAX:
            f.save()
            return f
        thumb_dir = make_path("thumbs")
        if not os.path.isdir(thumb_dir):
            os.makedirs(thumb_dir)
        suffix = ".{}".format(f.type.extension)
        with NamedTemporaryFile(suffix=suffix) as tmp:
            img.thumbnail((MAX, MAX), Image.ANTIALIAS)
            img.save(tmp)
            f.thumb = DjangoFile(tmp)
            f.save()
    except IOError:
        pass
    return f


def make_tripcode(text):
    """Makes tripcode from text."""
    text = text.replace("\\", "")
    trip = text.replace("#", "") if "##" in text else text
    trip = unicode(trip).encode("shift-jis")
    salt = trip + "H."
    salt = re.sub("/[^\.-z]/", ".", salt[1:3])
    salt = salt.translate(string.maketrans(":;<=>?@[\]^_`", "ABCDEFGabcdef"))
    return crypt(trip, salt)[-10:]


def strip_text(text, max_length=90):
    return text[:max_length] + u"..." if len(text) > max_length else text


def make_post_descriptions(posts):
    """Takes Post QuerySet and generates description to all posts."""
    posts = posts.values("thread__section__name", "thread__section__slug",
                         "id", "pid", "topic", "message")

    for post in posts:
        post["link"] = "/{slug}/{pid}".format(
            slug=post["thread__section__slug"], pid=post["pid"]
        )
        post["description"] = strip_text(
            post["topic"] or post["message"] or ">>{}".format(post["pid"])
        )
        yield post


def random_text(length=10):
    return "".join(
        choice(string.ascii_uppercase + string.digits)
        for x in xrange(length)
    )


def get_key(text):
    try:
        return sha1(text).hexdigest()
    except (UnicodeEncodeError, TypeError):
        return sha1(random_text()).hexdigest()


def parse_user_agent(user_agent):
    return httpagentparser.detect(user_agent)


def take_first(iterable):
    """Returns first element of iterable."""
    return [i[0] for i in iterable]


def from_timestamp(timestamp):
    """Convert timestamp to datetime object."""
    return str(datetime.fromtimestamp(int(timestamp)))


def timestamp_now():
    return int(time() * 100)


def print_flush(text):
    sys.stdout.write("\r" + text)
    sys.stdout.flush()
