from django.core import serializers
from board.models import *

class InsufficientRightsError(Exception):
    """Raises if user has insufficient rights for current operation."""
    pass

class InvalidKeyError(Exception):
    """Raises if user has entered invalid modkey or deletion password."""
    pass

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

@cached(60*60*24)
def sections(categories=False):
    """Gets list of board sections."""
    if not categories:
        return Section.objects.all().order_by('slug')
    obj = SectionGroup.objects.all().order_by('order')
    data = [] # http://goo.gl/CpPq6
    for g in obj:
        d = {
            'id' : g.id,
            'name' : g.name, 
            'order' : g.order, 
            'is_hidden' : g.is_hidden,
            'sections' : list(g.sections())
        }
        data.append(d)
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