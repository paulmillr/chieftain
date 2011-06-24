from random import randint
from datetime import datetime

from django.core.management.base import BaseCommand


def rand():
    return randint(0, 50000)


def make_posts(section, threads=100, posts=200):
    start = datetime.now()
    # ...
    print("{} posts in {}".format(posts, datetime.now() - start))


class Command(BaseCommand):
    def handle(self, *args, **options):
        make_posts(options["section"], options["posts"], options["thread"])
