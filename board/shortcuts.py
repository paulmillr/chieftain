import codecs
from django.core.paginator import InvalidPage, EmptyPage
from django.http import Http404
from django.template import RequestContext
from django.template.loader import render_to_string
from board.models import SectionGroup  # block recursive import

__all__ = ['get_page_or_404', 'add_sidebar', 'render_to_file']


def get_page_or_404(paginator, page):
    """Gets page from Paginator instance or raises Http404 error."""
    try:
        return paginator.page(page)
    except (InvalidPage, EmptyPage):
        raise Http404


def add_sidebar(context={}):
    """Updates context dictionary with sidebar."""
    return dict(context, navigation=SectionGroup.objects.tree())


def render_to_file(template, filename, request, context):
    """Renders template to filename."""
    with codecs.open(filename, 'w', 'utf-8') as f:
        f.write(render_to_string(template, context, RequestContext(request)))
