#!/usr/bin/env python
# encoding: utf-8
"""
wipe.py

Created by Paul Bagwell on 2011-04-16.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
import os
from django.db import connection
from django.core.cache import cache
from django.core.management.base import BaseCommand
from board.models import Section, Thread, Post, File


def generate(section='au', threads=100, posts=200):
    """Generates content for imageboard."""
    sect = Section.objects.get(slug=section)
    