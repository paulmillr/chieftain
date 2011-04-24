#!/usr/bin/env python
# encoding: utf-8
"""
admin.py

Created by Paul Bagwell on 2011-01-13.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from board import models
from django.contrib import admin


class ChoiceInline(admin.TabularInline):
    model = models.Choice
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

admin.site.register(models.Poll, PollAdmin)
admin.site.register(models.Choice)
admin.site.register(models.Vote)
admin.site.register(models.Thread, ThreadAdmin)
admin.site.register(models.Post, PostAdmin)
admin.site.register(models.File)
admin.site.register(models.FileTypeGroup)
admin.site.register(models.FileType)
admin.site.register(models.Section)
admin.site.register(models.SectionGroup)
admin.site.register(models.UserProfile)
admin.site.register(models.Wordfilter)
admin.site.register(models.DeniedIP, DeniedIPAdmin)
