from django.conf.urls.defaults import include, patterns
from django.contrib import admin
admin.autodiscover()

packages = {'packages': ('chieftain.board',), }

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^api/i18n/$', 'django.views.i18n.javascript_catalog', packages),
    (r'^api/1\.0/', include('api1.urls')),
    (r'^modpanel/', include('modpanel.urls')),
    (r'^pda/', include('pda.urls')),
    (r'^mobile/', include('mobile.urls')),
    (r'^', include('board.urls')),
)
