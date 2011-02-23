#!/usr/bin/env python
# encoding: utf-8
"""
views.py

Created by Paul Bagwell on 2011-02-22.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""

from django.contrib.auth.decorators import login_required
from board.models import Wordfilter, DeniedIP
from board.shortcuts import rtr

def is_mod(request, section_slug):
    u = request.user
    if u.is_authenticated():
        if u.is_superuser or section_slug in u.userprofile_set.get().modded():
            return True
    return False

def index(request):
    return rtr('modindex.html', request)

@login_required
def wordfilter(request):
    return rtr('wordfilter.html', request, {
        'wordlist': Wordfilter.objects.all()})
    
@login_required
def banlist(request):
    return rtr('banlist.html', request, {
        'banlist': DeniedIP.objects.all()})
