from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page
from functools import partial
from board import api
from board.models import *

def rtr(template, request, dictionary={}):
    dictionary.update({'navigation' : api.sections(True)})
    return render_to_response(template, dictionary, 
        context_instance=RequestContext(request))

#rtr = render_to_response

def make_thumb(image):
    """Makes image thumbnail"""
    pass

def index(request):
    """Main imageboard page"""
    return rtr('index.html', request)
    
def settings(request):
    """User settings page"""
    return rtr('settings.html', request)

def search(request):
    """Search page"""
    return rtr('index.html')
        
def ip_posts(request, ip, key, board=''):
    """Gets list of posts from some IP. Valid modkey needed"""
    return rtr('post_list.html', api.ip_posts(ip, key, board))

def post(request, pid, section=''):
    """Gets post"""
    pass

def section(request, section, page=1):
    """
    Gets 20 threads from current section with
    OP post and last 5 posts in each thread
    """
    try:
        s = Section.objects.get(slug__exact=section)
    except Section.DoesNotExist:
        raise Http404
    return rtr('section.html', request, {'threads' : s.page_threads(page), 'request' : {'page' : page}})

def thread(request, section, op_post):
    """Gets thread and its posts"""
    Post.objects.get(pk=op_post)
    if request.method == 'POST':
        pass
    return rtr('thread.html', request, {'data' : \
        api.thread(section, op_post)})