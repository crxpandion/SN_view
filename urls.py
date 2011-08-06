from django.conf.urls.defaults import patterns, include, url
from django.views.static import serve
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'spatoNet.views.inputName'),
    url(r'^inputName/$', 'spatoNet.views.inputName'),
    url(r'^inputNetwork/(?P<ID>\w{1,20})/$', 'spatoNet.views.inputNetwork'),
    url(r'^inputNetwork/$',  'spatoNet.views.inputName'), # this is not quite right...
    url(r'^viewNetwork/(?P<ID>\w{1,20})/$', 'spatoNet.views.viewNetwork'),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^getNetwork/(?P<ID>\w{1,20})/$', 'spatoNet.views.getNetwork'),


    

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
