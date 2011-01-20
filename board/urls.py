from django.conf.urls.defaults import *

urlpatterns = patterns('board.views', 
    (r'^$', 'index'),
    (r'^settings$', 'settings'),
    (r'^search/$', 'search'),
    (r'^(?P<section>\w+)/$', 'section', {'page' : 0}),
    (r'^(?P<section>\w+)/p/(?P<page>\d+)$', 'section'),
    (r'^(?P<section>\w+)/(?P<thread>\d+)$', 'thread'),
)