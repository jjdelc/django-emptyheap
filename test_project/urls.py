from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('registration.urls')),
    (r'^', include('emptyheap.urls')),
)

from django.conf import settings

if settings.DEBUG:
    from django.views.static import serve
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$',
            serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True})
        )
