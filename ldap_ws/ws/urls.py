from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^email/$',
        'ldap_ws.ws.views.info_by_email',
        name='info_by_email'),
    url(r'^cn/$',
        'ldap_ws.ws.views.info_by_cn',
        name='info_by_cn'),
    url(r'^(?P<username>\w+)/$',
        'ldap_ws.ws.views.info_by_username',
        name='info_by_username'),
    url(r'^$',
        'ldap_ws.ws.views.authenticate',
        name='authenticate'),
    # url(r'^ws/', include('ldap_ws.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
