from django.conf.urls.defaults import patterns

urlpatterns = patterns('mobile.views',
    (r'^$', 'index'),
    (r'^(?P<section_slug>\w+)/$', 'section', {'page': 1}),
    (r'^(?P<section_slug>\w+)/page(?P<page>\d+)$', 'section'),
    (r'^(?P<section_slug>\w+)/(?P<op_post>\d+)$', 'thread'),
)
