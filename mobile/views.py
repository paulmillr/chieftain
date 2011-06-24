from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from board.models import Post, Section
from board.shortcuts import get_page_or_404, add_sidebar


def index(request):
    return render(request, "mobile/index.html", add_sidebar())


def section(request, section_slug, page):
    s = get_object_or_404(Section, slug=section_slug)
    t = get_page_or_404(Paginator(s.threads(), s.ONPAGE), page)
    return render(request, "mobile/section.html", {"section": s,
        "threads": t})


def thread(request, section_slug, op_post):
    """Thread and its posts."""
    post = get_object_or_404(Post, thread__section__slug=section_slug,
        pid=op_post, is_deleted=False)
    thread = post.thread
    if not post.is_op_post:
        return redirect("../{}/{}#post{}".format(
            thread.section, thread.op_post.pid, post.pid))
    return render(request, "mobile/thread.html", {"thread": thread})
