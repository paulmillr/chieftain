from urllib import quote

from django.template import Library

register = Library()


@register.filter
def add_query_param(url, param):
    key, val = param.split("=") if "=" in param else (param, "")
    url += "&" if "?" in url else "?"
    url += key + "=" + quote(val)
