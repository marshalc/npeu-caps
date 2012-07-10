from django.conf.urls import patterns, include, url
import caps
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
#    url(r'^admin/caps/capsform/view/all/', caps.views.admin_view_all),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', 'caps.views.home', name='home'),
)
