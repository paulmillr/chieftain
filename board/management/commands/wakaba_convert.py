#!/usr/bin/env python
# encoding: utf-8
"""
wakaba_convert.py

Created by Paul Bagwell on 2011-04-16.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        prefix = args[0] if len(args) > 0 else 'comments_'
        w = WakabaConverter(connection, prefix)
        w.convert()
