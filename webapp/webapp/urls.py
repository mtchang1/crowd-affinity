from django.conf.urls import patterns, include, url
from crowd_affinity.views import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'webapp.views.home', name='home'),
    # url(r'^webapp/', include('webapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    # Serve static
      (r'^static/(?P<path>.*)$', 'django.views.static.serve',
              {'document_root': settings.STATIC_ROOT,
                       'show_indexes': True}),
    # urls
    (r'^designer/$', designer),
    
    (r'^start1/$', start1),
    (r'^answerQuestion/?$', answerQuestion),
    (r'^askQuestion/?$', askQuestion),
    (r'^rate/?$', rate),
    (r'^decide/?$', decide),
    (r'^linking/?$', linking),
    (r'^finish/?$', finish),

    (r'^start2/$', start2),
    (r'^write/?$', write),
    (r'^rewrite/?$', rewrite),
    (r'^rateSentence/?$', rateSentence),
    (r'^tag/?$', tag),

    )
