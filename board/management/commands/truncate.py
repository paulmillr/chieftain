import os
import shutil

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand

from board.models import Thread, Post, File


class Command(BaseCommand):
    def handle(self, *args, **options):
        for model in (Thread, Post, File):
            model.objects.all().delete()
            model.deleted_objects.all().delete()
        cache.clear()

        for dir in ("section", "thumbs"):
            dir = os.path.join(settings.MEDIA_ROOT, dir)
            shutil.rmtree(dir, ignore_errors=True)
        shutil.rmtree("cache", ignore_errors=True)
