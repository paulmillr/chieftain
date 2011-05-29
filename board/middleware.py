from django.template import RequestContext
from django.template.loader import render_to_string
from django.http import HttpResponseForbidden
from api1.views import SettingResource, FeedResource, HideResource
from board.models import DeniedIP

__all__ = ['set_session_defaults', 'SessionDefaultsMiddleware',
    'DenyMiddleware', 'DisableCSRFMiddleware']


METHODS = ('GET', 'POST', 'UPDATE', 'DELETE')
WHITELIST = ()


def set_session_defaults(request):
    for i in [SettingResource, FeedResource, HideResource]:
        default = type(i.default)()  # prevent errors due to mutability
        request.session.setdefault(i.storage_name, default)


class SessionDefaultsMiddleware(object):
    def process_request(self, request):
        set_session_defaults(request)


def ip_in(ip, model):
    """Returns True if the given ip address is in one of the ban models."""
    try:
        for i in model.objects.all():
            if ip in i.network():
                return i.reason if i.reason else ''
    except ValueError:
        pass
    return False


def get_ip(request):
    """Gets the true client IP address of the request.

       Contains proxy handling involving HTTP_X_FORWARDED_FOR
       and multiple addresses.
    """
    ip = request.META['REMOTE_ADDR']
    if not ip or ip == '127.0.0.1' and 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    try:  # choose first of (possibly) multiple values
        return ip.replace(',', '').split()[0]
    except IndexError:
        return request.META['REMOTE_ADDR']


def forbid(request, reason=''):
    """
    Forbids a user to access the site
    Cleans up their session (if it exists)
    Returns a templated HttpResponseForbidden when banning requests
    Override the `403.html` template to customize the error report
    """
    for k in request.session.keys():
        del request.session[k]
    return HttpResponseForbidden(render_to_string('banned.html',
        {'reason': reason}, context_instance=RequestContext(request)))


class DenyMiddleware(object):
    """Forbids any request if they are in the DeniedIP list."""
    def process_request(self, request):
        ip = get_ip(request)
        if not request.method in METHODS or ip in WHITELIST:
            return False
        reason = ip_in(ip, DeniedIP)
        # not simply 'if reason:' because it could return empty string
        if reason is not False:
            return forbid(request, reason)


class DisableCSRFMiddleware(object):
    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)
        return None
