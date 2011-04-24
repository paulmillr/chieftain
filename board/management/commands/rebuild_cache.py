#!/usr/bin/env python
# encoding: utf-8
"""
rebuild_cache.py

Created by Paul Bagwell on 2011-04-16.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
import os
import shutil
from django.core.management.base import BaseCommand
from board.models import Thread, Post


class Command(BaseCommand):
    def handle(self, *args, **options):
        """Rebuilds cache."""
        shutil.rmtree('cache', ignore_errors=True)
        threads = Thread.objects.all()
        posts = Post.objects.all()
        for c, tr in enumerate(threads):
            tr.save()
            if c % 50 == 0:
                print 'Rendered thread {0}'.format(c)
        for c, post in enumerate(posts):
            post.save()
            if c % 250 == 0:
                print 'Rendered post {0}'.format(c)
        cache.clear()
