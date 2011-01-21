from django.conf.urls.defaults import *

urlpatterns = patterns('board.views', 
    (r'^$', 'index'),
    (r'^settings$', 'settings'),
    (r'^search/$', 'search'),
    (r'^(?P<section>\w+)/$', 'section', {'page' : 1}),
    (r'^(?P<section>\w+)/page(?P<page>\d+)$', 'section'),
    (r'^(?P<section>\w+)/(?P<thread>\d+)$', 'thread'),
)