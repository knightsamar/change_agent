from manage_feedback.models import feedbackQuestion,feedbackQuestionOption,feedbackForm,feedbackAbout
from django.contrib import admin
from ldap_login.models import *
from give_feedback.models import feedbackSubmission
from django.http import HttpResponse
#for displaying options directly underneath the question when creating or editing
class feedbackQuestionOptionsInline(admin.TabularInline):
    model = feedbackQuestionOption;
    extra = 4;

class feedbackQuestionAdmin(admin.ModelAdmin):
    inlines = [feedbackQuestionOptionsInline];
    
class feedbackFormAdmin(admin.ModelAdmin):
    actions = ['duplicateForm'];
    actions = ['notFilled']

    def duplicateForm(self, request, queryset):
        for existing_form in queryset:
             new_form = feedbackForm();
             new_form.title = "Copy of " + existing_form.title;
             new_form.deadline_for_filling = existing_form.deadline_for_filling;
             new_form.about = existing_form.about;
             new_form.save();
             for q in existing_form.questions.all():
                 new_form.questions.add(q);
             
             for g in existing_form.allowed_groups.all():
                  new_form.allowed_groups.add(g);
    
             #new_form.allowed_groups = existing_form.allowed_groups;

    duplicateForm.short_description = "Duplicate this form";


    def notFilled(self, request, queryset):
        for existing_form in queryset:
            user_all=list()
            groups=existing_form.allowed_groups.values()
            for g in groups:
                # to extract users who were supposed to fill the form
                u=user.objects.filter(groups=g['id'])
                user_all.extend(u)
            #now from this list.. remove ppl who have filled the form...!!
            forms=feedbackSubmission.objects.filter(feedbackForm=existing_form)
            for f in forms:
                user_all.remove(f.submitter)
            print ".....",existing_form.title,"......"
            print user_all
        return HttpResponse(existing_form.title)
    notFilled.short_description = "People who have not filled this form";
         
admin.site.register(feedbackQuestion,feedbackQuestionAdmin);

#enable in admin site the following other things
admin.site.register(feedbackQuestionOption);
admin.site.register(feedbackForm,feedbackFormAdmin);
admin.site.register(feedbackAbout);

