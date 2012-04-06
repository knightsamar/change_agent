#urls for give_feedback app

from django.conf.urls.defaults import *
from manage_feedback.models import feedbackForm

#info_dict = {
#	'queryset':
info_dict = {
	'queryset' : feedbackForm.objects.all(),
	#should be changed to feedbackForm.allowedforCurrenUser() which will automatically pass the username from the session and bring only those forms....that method is to be defined in the model for feedbackForm
	}

#urlpatterns = patterns('',
#	(r'^$','django.views.generic.list_detail.object_list',info_dict),
#	);


