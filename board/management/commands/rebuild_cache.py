from shutil import rmtree
from itertools import chain

from django.core.cache import cache
from django.core.management.base import BaseCommand

from board.tools import print_flush
from board.models import Thread, Post


class Command(BaseCommand):
    def handle(self, *args, **options):
        """Rebuild the cache."""
        shutil.rmtree("cache", ignore_errors=True)
        for obj in chain(Thread.objects.all(), Post.objects.all()):
            obj.save()
        cache.clear()
