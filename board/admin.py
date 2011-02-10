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


class IPAdmin(admin.ModelAdmin):
    search_fields = ('ip',)

admin.site.register(Thread)
admin.site.register(Post)
admin.site.register(File)
admin.site.register(FileCategory)
admin.site.register(FileType)
admin.site.register(Section)
admin.site.register(SectionGroup)
admin.site.register(User)


if 'board.middleware.DenyMiddleware' in settings.MIDDLEWARE_CLASSES:
    admin.site.register(DeniedIP, IPAdmin)

if 'board.middleware.AllowMiddleware' in settings.MIDDLEWARE_CLASSES:
    admin.site.register(AllowedIP, IPAdmin)
