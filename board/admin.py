#!/usr/bin/env python
# encoding: utf-8
"""
admin.py

Created by Paul Bagwell on 2011-01-13.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from board.models import *
from django.contrib import admin

admin.site.register(Thread)
admin.site.register(Post)
admin.site.register(File)
admin.site.register(FileCategory)
admin.site.register(FileType)
admin.site.register(Section)
admin.site.register(SectionGroup)
admin.site.register(User)
