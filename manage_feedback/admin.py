from manage_feedback.models import feedbackQuestion,feedbackQuestionOption,feedbackForm,feedbackAbout
from django.contrib import admin


#for displaying options directly underneath the question when creating or editing
class feedbackQuestionOptionsInline(admin.TabularInline):
    model = feedbackQuestionOption;
    extra = 4;

class feedbackQuestionAdmin(admin.ModelAdmin):
    inlines = [feedbackQuestionOptionsInline];

admin.site.register(feedbackQuestion,feedbackQuestionAdmin);

#enable in admin site the following other things
admin.site.register(feedbackQuestionOption);
admin.site.register(feedbackForm);
admin.site.register(feedbackAbout);

