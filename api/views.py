from django.core.cache import cache
from django.core import serializers
from board.models import *
from itertools import chain

def cache_f(func):
    """Decorator for caching."""
    pass

class InsufficientRightsError(Exception):
    """Raises if user has insufficient rights for current operation."""
    pass

class InvalidKeyError(Exception):
    """Raises if user has entered invalid modkey or deletion password."""
    pass

def valid_key(key, post='', section=''):
    """Checks if current key is valid moderation key"""
    user = User.objects.get(key__exact=key)
    if post:
        if isinstance(post, str): # we've got not QuerySet
            post = get_post(post, section) # make QuerySet
            if not post:
                return False
        if post.password == key: # post is touched by user
            return True
        else:
            if user: # post is touched by mod
                if post.section in user.sections and post.key == user.key: # TODO: test
                    return True
    else:
        if section:
            if section in user.sections:
                return True
        else:
            return bool(user)
    return False

def new(section, poster, tripcode, email, topic, password, file, 
		thread, text):
    """Creates new thread"""
    if request.method == 'POST':
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        # get id of newest section post
        last_post = Post.objects.values_list('pid', flat=True)[-1]['pid']
        Post.objects.create(section=section, pid=last_post, ip=ip)

def captcha():
    """docstring for captcha"""
    pass 
        
def ip_posts(ip, key, board=''):
    """Gets list of posts from some IP. Valid modkey needed."""
    if key in valid_modkeys():
        params = dict(ip__exact=ip, board__exact=board)
        if board == '':
            params.pop(board__exact)
        return Post.objects.filter(**params)
    else:
        raise InvalidKeyError

def new_post(**kwargs):
    """Creates new post"""
    pass

def is_op_post(post):
    """Checks if current post starts thread"""
    if isinstance(post, str):
        post = Post.objects.get(pk=post)
    return post.is_op_post

def del_post(id, key):
    """Removes some post."""
    p = Post.objects.get(pk=id)
    if valid_key(key, p):
        if is_op_post(p): # if current post is OP-post
            thread(p.pid, p.section).delete()
        else:
            p.delete()
    else:
        raise InvalidKeyError

def sections(categories=False):
    """Gets list of board sections."""
    if not categories:
        return Section.objects.all().order_by('slug')
    data = cache.get('section_groups')
    if not data:
        obj = SectionGroup.objects.all().order_by('order')
        data = [] # http://goo.gl/CpPq6
        # sorry, i've wasted two days looking for
        # HOW TO fully cache foreign key models
        for g in obj:
            d = {
                'id' : g.id,
                'name' : g.name, 
                'order' : g.order, 
                'is_hidden' : g.is_hidden,
                'sections' : list(g.sections())
            }
            data.append(d)
        cache.set('section_groups', data, 60*60*24)
    return data

def post(id, section_slug=''):
    """Gets post by its primary key.
    
       There can be two variants:
       - Getting by primary key:
       >>> post(r, 85930)
       - Getting by board slug and board post id
       >>> post(r, 40200, 'b')
    """
    args = {}
    if section_slug:
        args['section__slug__iexact'] = section_slug
        args['pid'] = id
    else:
        args['pk'] = id
    return Post.objects.get(**args)

def section(section, page=1):
    """
    Gets 20 threads from current section with
    OP post and last 5 posts in each thread.
    """
    onpage = 20
    lp = 5 # number of last posts
    filt = {'is_op_post' : True}
    if (isinstance(section, basestring)):
        filt.update({'section__slug__iexact' : section})
    else:
        filt.update({'section' : section})
    
    op_posts = Post.objects.filter(**filt).order_by('id')
    threads = []
    for post in op_posts:
        t = Thread.objects.get(id=post.thread_id)
        ps = t.post_set
        stop = ps.count()
        if stop <= lp: # if we got thread with less posts than lp
            threads.append(t)
        else:
            start = stop - lp
            all = ps.all()
            threads.append([all[0]] + list(all[start:stop])) # select last 5 posts
    return threads
    
def thread(op_post, section):
    """Gets thread and its posts"""
    return Post.objects.filter(thread=post(op_post, section).thread_id)
