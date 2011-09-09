from django.conf.urls.defaults import patterns
from djangorestframework.views import ListOrCreateModelView, InstanceModelView

from .resources import *
from .views import *

urlpatterns = patterns("api1.views", (r"^$", "api"),

    (r"^setting/$", SettingRootView.as_view()),
    (r"^setting/(?P<key>[\w\d]+)$", SettingView.as_view()),

    (r"^feed/$", FeedRootView.as_view()),
    (r"^feed/(?P<key>[\d]+)$", FeedView.as_view()),

    (r"^hidden/$", HideRootView.as_view()),
    (r"^hidden/(?P<key>[\d]+)?$", HideView.as_view()),

    (r"^thread/$",
        ListOrCreateModelView.as_view(resource=ThreadResource)),
    (r"^thread/(?P<section__slug>\w+)/$",
        ListOrCreateModelView.as_view(resource=ThreadResource)),
    (r"^thread/(?P<id>\d+)$",
        ThreadInstanceView.as_view(resource=ThreadResource)),
    (r"^thread/(?P<section__slug>\w+)/(?P<id>\d+)$",
        ThreadInstanceView.as_view(resource=ThreadResource)),

    (r"^post/$",
        PostListOrCreateView.as_view(resource=PostResource)),
    (r"^post/(?P<thread__section__slug>\w+)/$",
        PostListOrCreateView.as_view(resource=PostResource)),
    (r"^post/(?P<thread__section__slug>\w+)/first/$",
        PostListOrCreateView.as_view(resource=PostResource),
        {"is_op_post": True}),
    (r"^post/(?P<id>\d+)$",
        PostInstanceView.as_view(resource=PostResource)),
    (r"^post/(?P<thread__section__slug>\w+)/(?P<pid>\d+)$",
        PostInstanceView.as_view(resource=PostResource)),

    (r"^section/$",
        ListOrCreateModelView.as_view(resource=SectionResource)),
    (r"^section/(?P<id>\d+)$",
        InstanceModelView.as_view(resource=SectionResource)),
    (r"^section/(?P<slug>\w+)",
        InstanceModelView.as_view(resource=SectionResource)),

    (r"^sectiongroup/",
        ListOrCreateModelView.as_view(resource=SectionGroupResource)),
    (r"^sectiongroup/(?P<id>\d+)",
        InstanceModelView.as_view(resource=SectionGroupResource)),

    (r"^file/$",
        ListOrCreateModelView.as_view(resource=FileResource)),
    (r"^file/(?P<id>\d+)$",
        FileInstanceView.as_view(resource=FileResource)),
    (r"^file/random_image/(?P<count>\d{1,2})",
        RandomImageView.as_view(resource=FileResource)),

    (r"^filetype/(?P<id>\d+)$",
        InstanceModelView.as_view(resource=FileTypeResource)),
    (r"^filetype/(?P<extension>[\w\d]+)$",
        InstanceModelView.as_view(resource=FileTypeResource)),

    (r"^filetypegroup/$",
        ListOrCreateModelView.as_view(resource=FileTypeGroupResource)),
    (r"^filetypegroup/(?P<id>\d+)$",
        InstanceModelView.as_view(resource=FileTypeGroupResource)),
)
