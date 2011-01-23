from django.conf.urls.defaults import *

urlpatterns = patterns('board.views', 
    (r'^$', 'index'),
    (r'^settings$', 'settings'),
    (r'^faq$', 'faq'),
    (r'^search/$', 'search'),
    (r'^(?P<section>\w+)/$', 'section', {'page' : 1}),
    (r'^(?P<section>\w+)/page(?P<page>\d+)$', 'section'),
    (r'^(?P<section>\w+)/(?P<op_post>\d+)$', 'thread'),
)