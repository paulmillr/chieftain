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

