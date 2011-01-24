from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.forms.models import modelformset_factory
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page
from functools import partial
from board import api
from board.models import *
import sys

def rtr(template, request, dictionary={}):
    dictionary.update({'navigation' : SectionGroup.objects.sections()})
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

def faq(request):
    return rtr('faq.html', request)

def section(request, section, page=1):
    """
    Gets 20 threads from current section with
    OP post and last 5 posts in each thread
    """
    try:
        s = Section.objects.get(slug__exact=section)
        t = s.page_threads(page)
    except (Section.DoesNotExist, InvalidPage, EmptyPage):
        raise Http404
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            model = form.save(commit=False)
            if 'REMOTE_ADDR' in request.META:
                model.ip = request.META['REMOTE_ADDR']
            model.file_count = len(request.FILES)
            model.is_op_post = True
            model.date = datetime.now()
            t = Thread(section_id=request.POST['section'], bump=model.date)
            model.pid = t.section.incr_cache()
            t.save(no_cache_rebuild=True)
            model.thread = t
            model.save()
            t.save() # rebuild cache
            return HttpResponseRedirect('{0}#post{1}'.format(
                model.pid, model.pid))
        else:
            return rtr('error.html', request, {'errors' : form.errors})
                
    form = PostForm()
    return rtr('section.html', request, {'threads' : t, 'section' : s, 
        'form' : form})

def thread(request, section, op_post):
    """Gets thread and its posts"""
    args = {'thread__section__slug' : section, 'pid' : op_post,
        'is_op_post' : True}
    try:
        tid = Post.objects.thread_id(section, op_post)
        t = Thread.objects.get(id=tid)
    except (Post.DoesNotExist):
        try:
            args['is_op_post'] = False
            t = Post.objects.get(**args).thread
            post = op_post
        except (Post.DoesNotExist):
            raise Http404
        else:
            return redirect('/{0}/{1}#post{2}'.format(\
                t.section, t.op_post().pid, post))
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            model = form.save(commit=False)
            t = Thread.objects.get(id=request.POST['thread'])
            if 'REMOTE_ADDR' in request.META:
                model.ip = request.META['REMOTE_ADDR']
            model.pid = t.section.incr_cache()
            model.file_count = len(request.FILES)
            model.is_op_post = False
            model.date = datetime.now()
            model.save()
            if model.email != 'sage':
                t.bump = model.date
                t.save()
            return HttpResponseRedirect('{0}#post{1}'.format(
                t.op_post().pid, model.pid))
        else:
            return rtr('error.html', request, {'errors' : form.errors})
    else:
        form = PostForm()
    return rtr('thread.html', request, {'thread' : t, 'form' : form})