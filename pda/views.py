from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from board.models import Post, Section
from board.shortcuts import get_page_or_404, add_sidebar


def index(request):
    return render(request, "pda/index.html", add_sidebar())


def section(request, section_slug, page):
    s = get_object_or_404(Section, slug=section_slug)
    p = get_page_or_404(Paginator(s.op_posts(), s.ONPAGE), page)
    return render(request, "pda/section.html", {"section": s,
        "posts": p})


def thread(request, section_slug, op_post):
    """Thread and its posts."""
    post = get_object_or_404(Post, thread__section__slug=section_slug,
        pid=op_post, is_deleted=False)
    thread = post.thread
    if not post.is_op_post:
        return redirect("/{}/{}#post{}".format(
            thread.section, thread.op_post.pid, post.pid))
    return render(request, "pda/thread.html", {"thread": thread})
