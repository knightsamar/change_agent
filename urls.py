from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^change_agent/', include('change_agent.foo.urls')),
    (r'^give_feedback/$','give_feedback.views.index'),
    (r'^give_feedback/(?P<form>\d+)/$','give_feedback.views.show_form'),

    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    #(r'^/', include(ldap_login.views.login)), #default is login page

#    (r'^/feedback_about/'
)
