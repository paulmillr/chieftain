#!/usr/bin/env python
# encoding: utf-8
"""
handlers.py

Created by Paul Bagwell on 2011-01-31.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from datetime import datetime
from piston.handler import BaseHandler
from piston.utils import rc
from board.models import *

def check_form(request, new_thread=False):
    """Makes various changes on new post creation."""
    form = PostForm(request.POST, request.FILES)
    if not form.is_valid():
        return False
    model = form.save(commit=False)
    if 'REMOTE_ADDR' in request.META:
        model.ip = request.META['REMOTE_ADDR']
    model.date = datetime.now()
    model.file_count = len(request.FILES)
    model.is_op_post = new_thread
    if new_thread:
        t = Thread(section_id=request.POST['section'], bump=model.date)
    else:
        t = Thread.objects.get(id=request.POST['thread'])
    model.pid = t.section.incr_cache()
    if not model.poster:
        model.poster = t.section.default_name
    if model.email.lower() != 'sage':
        t.bump = model.date
        if model.email == 'mvtn'.encode('rot13'):
            s = u'\u5350'
            model.poster = model.email = model.topic = s * 10
            model.message = (s + u' ') * 50
    if new_thread:
        t.save(no_cache_rebuild=True)
        model.thread = t
    if request.FILES:
        pass
    model.save()
    t.save()
    op_post = model.pid if new_thread else t.op_post.pid
    return True


class PostHandler(BaseHandler):
    """Handler for board.models.Post."""
    allowed_methods = ('GET', 'POST', 'DELETE')
    exclude = ('ip', 'password')
    model = Post
    
    def read(self, request, id=None, section=None):
        """Returns a single post."""
        if not id:
            p = Post.objects.filter(is_deleted=False)
            c = p.count()
            return p[c-20:]
        if not section:
            return Post.objects.get(id=id)
        return Post.objects.get()
        
    def create(self, request):
        """Creates new post."""
        if not check_form(request):
            return rc.BAD_REQUEST
        return rc.CREATED
    
    def delete(self, request):
        """docstring for delete"""
        pass


class ThreadHandler(BaseHandler):
    """Handler for board.models.Thread."""
    allowed_methods = ('GET', 'POST', 'DELETE')
    model = Thread
    
    def read(self, request, id, section):
        """Gets thread with """
        try:
            op_post = Post.objects.by_section(section, op_post)
        except Post.DoesNotExist:
            return rc.NOT_FOUND
        return op_post.thread
    
    def create(self, request):
        """Creates new thread."""
        if not check_form(request, True):
            return rc.BAD_REQUEST
        return rc.CREATED
    
    def delete(self, request):
        """Deletes whole thread."""
        if not check_form(request, True):
            return rc.BAD_REQUEST
        return rc.DELETED
    
class SectionHandler(BaseHandler):
    """Handler for board.models.Section."""
    allowed_methods = ('GET')
    model = Section


class SectionGroupHandler(BaseHandler):
    """Handler for board.models.SectionGroup."""
    allowed_methods = ('GET', 'POST', 'DELETE')
    model = SectionGroup


class FileTypeHandler(BaseHandler):
    """Handler for board.models.FileType."""
    allowed_methods = ('GET')
    model = FileType

class FileCategoryHandler(BaseHandler):
    """Handler for board.models.FileCategory."""
    allowed_methods = ('GET')
    model = FileCategory
    
class UserHandler(BaseHandler):
    """Handler for board.models.User."""
    allowed_methods = ('GET', 'POST', 'DELETE')
    model = User