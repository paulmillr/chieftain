from django.conf.urls.defaults import patterns

urlpatterns = patterns("modpanel.views",
    (r"^$", "index"),
    (r"^wordfilter$", "wordfilter"),
    (r"^banlist$", "banlist"),
    #(r"^(?P<section>\w+)/$", "section", {"page": 1}),
    #(r"^(?P<section>\w+)/page(?P<page>\d+)$", "section"),
    #(r"^(?P<section>\w+)/(?P<op_post>\d+)$", "thread"),
)
