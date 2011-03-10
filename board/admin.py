#!/usr/bin/env python
# encoding: utf-8
"""
admin.py

Created by Paul Bagwell on 2011-01-13.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from board.models import *
from django.contrib import admin


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3
    exclude = ('vote_count',)


class PollAdmin(admin.ModelAdmin):
    list_display = ('question', 'expires')
    inlines = [ChoiceInline]


class ThreadAdmin(admin.ModelAdmin):
    """Admin controller for threads."""
    exclude = ('html',)


class PostAdmin(admin.ModelAdmin):
    search_fields = ('pid', 'thread__section__slug')
    exclude = ('html', 'is_op_post')


class DeniedIPAdmin(admin.ModelAdmin):
    search_fields = ('ip',)

admin.site.register(Poll, PollAdmin)
admin.site.register(Choice)
admin.site.register(Vote)
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
