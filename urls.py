from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
	#(r'^modpanel/', include('mod.urls')),
    (r'^api/', include('webapi.urls')),
    (r'^', include('board.urls')),
)
