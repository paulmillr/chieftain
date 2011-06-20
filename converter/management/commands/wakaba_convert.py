#!/usr/bin/env python
# encoding: utf-8
from django.core.management.base import BaseCommand
from board.models import Thread
from converter.models import WakabaInitializer, WakabaConverter, WakabaPost


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not WakabaPost.objects.count():
            i = WakabaInitializer()
            i.convert()
        w = WakabaConverter()
        w.convert()
