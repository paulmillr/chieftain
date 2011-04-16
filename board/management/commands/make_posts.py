#!/usr/bin/env python
# encoding: utf-8
"""
make_posts.py

Created by Paul Bagwell on 2011-04-16.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
import sys
import random
from board import models
from datetime import datetime
from random import random
from django.db import connection
from django.core.cache import cache
from django.core.management.base import BaseCommand


def rand():
    return str(int(random() * 100000) % 50000)


def wipe(posts=10, thread=False):
    # >>> wipe(50000, 'b')
    # 50000 posts in 0:34:54.923063
    start = datetime.now()

    print '{0} posts in {1}'.format(posts, datetime.now() - start)


class Command(BaseCommand):
    def handle(self, *args, **options):
        wipe(options['posts'], options['thread'])
