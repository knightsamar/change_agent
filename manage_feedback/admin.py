from manage_feedback.models import feedbackQuestion,feedbackQuestionOption,feedbackForm,feedbackAbout
from django.contrib import admin

#enable in admin site the following
admin.site.register(feedbackQuestion);
admin.site.register(feedbackQuestionOption);
admin.site.register(feedbackForm);
admin.site.register(feedbackAbout);


