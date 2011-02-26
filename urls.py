from django.conf.urls.defaults import *
from django.contrib import admin
from piston.resource import Resource
from board.handlers import PostHandler
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^api/i18n/(?P<packages>\S+?)$', 'django.views.i18n.javascript_catalog'),
    (r'^api/', include('api.urls')),
    (r'^modpanel/', include('modpanel.urls')),
    #(r'^mobile/', include('mobile.urls')),
    (r'^', include('board.urls')),
)
