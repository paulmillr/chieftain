#!/usr/bin/env python
# encoding: utf-8
"""
wakaba_convert.py

Created by Paul Bagwell on 2011-04-16.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
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
