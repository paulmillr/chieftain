# coding: utf-8
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
    dictionary.update({'navigation': SectionGroup.objects.sections()})
    return render_to_response(template, dictionary, 
        context_instance=RequestContext(request))

def parse(st):
    patterns = [
        (r'\*\*(.*?)\*\*', r'<strong>\1</strong>'),
        (r'\*(.*?)\*', r'<em>\1</em>'),
        (r'%%(.*?)%%', r'<spoiler>\1</spoiler>')
    ]
    r = [(re.compile(i[0]), re.compile(i[1])) for i in patterns]
    map(re.compile, )
    for pattern in patterns:
        d = re.finditer(pattern[0], st)
        for match in d:
            start, stop = match.start(), match.end()
            res = ''
            res = re.sub(pattern[0], pattern[1], st[start:stop])
            st = st[:start] + res + st[stop:]
    return st

def check_form(request, new_thread=False):
    """Makes various changes on new post creation."""
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
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
        if model.poster == '':
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
        model.save()
        t.save()
        
        op_post = model.pid if new_thread else t.op_post().pid
        return HttpResponseRedirect('{0}#post{1}'.format(op_post, model.pid))
    else:
        return rtr('error.html', request, {'errors': form.errors})


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
    if request.method == 'POST':
        return check_form(request, True)
    try:
        s = Section.objects.get(slug__exact=section)
        t = s.page_threads(page)
    except (Section.DoesNotExist, InvalidPage, EmptyPage):
        raise Http404
    form = PostForm()
    return rtr('section.html', request, {'threads': t, 'section': s, 
        'form': form})

def thread(request, section, op_post):
    """Gets thread and its posts"""
    if request.method == 'POST':
        return check_form(request, False)
    args = {'thread__section__slug': section, 'pid': op_post,
        'is_op_post': True}
    try:
        tid = Post.objects.thread_id(section, op_post)
        t = Thread.objects.get(id=tid)
    except (Post.DoesNotExist):
        try:
            args['is_op_post'] = False
            t = Post.objects.get(**args).thread
            post = op_post
        except Post.DoesNotExist:
            raise Http404
        return redirect('/{0}/{1}#post{2}'.format(\
                t.section, t.op_post().pid, post))
    else:
        form = PostForm()
    return rtr('thread.html', request, {'thread': t, 'form': form})