from django.conf.urls.defaults import *
#from ldapAuthBackend import authenticate;
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^change_agent/', include('change_agent.foo.urls')),
    (r'^change_agent/','ldap_login.views.login'),
    (r'^$','ldap_login.views.login'),
    (r'^give_feedback/$','give_feedback.views.index'),
    (r'^manage_feedback/admin$','manage_feedback.views.adminindex'),
    (r'^manage_feedback/createforms$','manage_feedback.views.createmassforms'),
    (r'^ldap_login/$','ldap_login.views.login'), #for authentication
    (r'^ldap_login/logout$','ldap_login.views.logout'), #for loggin out
    (r'^ldap_login/passwordHelp$','ldap_login.views.passwordHelp'),
    (r'^manage_feedback/(?P<errorcode>\d+)/error/$','manage_feedback.views.error'), 
    (r'^manage_feedback/notfilled/$','manage_feedback.views.notFilled'), 
    (r'^manage_feedback/studentsummary$','manage_feedback.views.stusummary'), 
    (r'^give_feedback/(?P<form>\d+)/show/$','give_feedback.views.show'), 
    (r'^give_feedback/(?P<form>\d+)/edit/$','give_feedback.views.editsubmit'), 
    (r'^manage_feedback/(?P<formID>\d+)/feedbackAbout/$','manage_feedback.views.summary'), 
    (r'^give_feedback/edit/$','give_feedback.views.edit'),
    (r'^give_feedback/edit/$','give_feedback.views.edit'),
    (r'^give_feedback/(?P<submissionID>\d+)/preview.html/$','give_feedback.views.preview'),
    #(r'^manage_feedback/admin/deadline/$','manage_feedback.admin.FeedbackFormAdmin.ChangeDeadline'),
	#(r'^give_feedback/(?P<form>\d+)/preview/$','give_feedback.views.preview'),
	(r'^give_feedback/(?P<form>\d+)/submit/$','give_feedback.views.submit'),    
    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
     
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    
    #example app for trying out social auth
    (r'^social_auth/logged-in/', 'socialauth.views.afterglow'),
    (r'^social_auth/logout/','socialauth.views.logout'),
    #(r'^/', include(ldap_login.views.login)), #default is login page
    (r'', include('social_auth.urls')),
)

if settings.DEBUG:
	# Serve static files in debug.
	urlpatterns += patterns('',
		(r'^change_agent_media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT,'show_indexes' : True}),
)
