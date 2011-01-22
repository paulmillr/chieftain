from board.models import *

def generate(threads=100, posts=200):
    """docstring for generate"""
    sect = Section.objects.get(pk=1)
    for t in range(1, threads):
        if t < 10: time = '0'+str(t)
        else:
            if t > 99:
                time = 99
            else:
                time = t
        targs = {
            'bump' : '20{0!s}-01-20 14:12:13'.format(time),
            'section' : sect,
        }
        tr = Thread(**targs)
        tr.save()
        for p in range(1, posts):
            iop = 1 if p == 1 else 0
            args = {
                'pid' : p * t + 10,
                'thread' : tr,
                'is_op_post' : iop,
                'ip' : '127.{0!s}.{1!s}.1'.format(t, p),
                'topic' : 'Thread {0!s}, post {1!s}'.format(t, p),
                'message' : 'Hi, guyz! It is threadpost {0!s}'.format(t * p),
            }
            post = Post(**args)
            post.save()