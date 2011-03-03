from django.conf.urls.defaults import *
from django.contrib import admin
from piston.resource import Resource
from board.handlers import PostHandler
admin.autodiscover()

packages = {'packages': ('klipped.board',), }

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^api/i18n/$', 'django.views.i18n.javascript_catalog', packages),
    (r'^api/', include('api.urls')),
    (r'^modpanel/', include('modpanel.urls')),
    (r'^pda/', include('pda.urls')),
    (r'^mobile/', include('mobile.urls')),
    (r'^', include('board.urls')),
)
