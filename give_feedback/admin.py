from give_feedback.models import feedbackSubmission, feedbackSubmissionAnswer
from django.contrib import admin

class feedbackSubmissionAdmin(admin.ModelAdmin):
    search_fields = ['submitter'];

#enable in admin site the following
admin.site.register(feedbackSubmission);
admin.site.register(feedbackSubmissionAnswer);


