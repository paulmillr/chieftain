from piston.handler import BaseHandler
from board.models import Post

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
            #handle_uploaded_file(request.FILES['file'], t.section, t, model.pid)
            #f = File(post=model, mime='image/jpeg')
        model.save()
        t.save()
        op_post = model.pid if new_thread else t.op_post.pid
        return HttpResponseRedirect('{0}#post{1}'.format(op_post, model.pid))
    else:
        return rtr('error.html', request, {'errors': form.errors})

class PostHandler(BaseHandler):
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
        check_form(request)