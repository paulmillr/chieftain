#!/usr/bin/env python
# encoding: utf-8
"""
admin.py

Created by Paul Bagwell on 2011-01-13.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from klipped import settings
from board.models import *
from django.contrib import admin


class DeniedIPAdmin(admin.ModelAdmin):
    search_fields = ('ip',)


class ThreadAdmin(admin.ModelAdmin):
    """Admin controller for threads"""
    exclude = ('html',)


class PostAdmin(admin.ModelAdmin):
    search_fields = ('pid', 'thread__section__slug')
    exclude = ('html',)

admin.site.register(Thread, ThreadAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(File)
admin.site.register(FileTypeGroup)
admin.site.register(FileType)
admin.site.register(Section)
admin.site.register(SectionGroup)
admin.site.register(UserProfile)
admin.site.register(Wordfilter)
admin.site.register(DeniedIP, DeniedIPAdmin)
