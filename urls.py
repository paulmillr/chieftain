from django.conf.urls.defaults import *
from django.contrib import admin
from piston.resource import Resource
from board.handlers import PostHandler
admin.autodiscover()

post_handler = Resource(PostHandler)

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
#    (r'^modpanel/', include('mod.urls')),
    (r'^api/(?P<id>\d+)', include('board.api.urls')),
    (r'^', include('board.urls')),
)
