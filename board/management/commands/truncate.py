import os
import shutil
from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand
from board.models import Thread, Post, File


class Command(BaseCommand):
    def handle(self, *args, **options):
        for m in [Thread, Post, File]:
            m.objects.all().delete()
            m.deleted_objects.all().delete()
        cache.clear()
        make_path = lambda x: os.path.join(settings.MEDIA_ROOT, x)
        for d in [make_path(x) for x in ['section', 'thumbs']]:
            shutil.rmtree(d, ignore_errors=True)
        shutil.rmtree('cache', ignore_errors=True)
