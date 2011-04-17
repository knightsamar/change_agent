from manage_feedback.models import feedbackQuestion,feedbackQuestionOption,feedbackForm,feedbackAbout
from django.contrib import admin


#for displaying options directly underneath the question when creating or editing
class feedbackQuestionOptionsInline(admin.TabularInline):
    model = feedbackQuestionOption;
    extra = 4;

class feedbackQuestionAdmin(admin.ModelAdmin):
    inlines = [feedbackQuestionOptionsInline];
    
class feedbackFormAdmin(admin.ModelAdmin):
    actions = ['duplicateForm'];

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
        
admin.site.register(feedbackQuestion,feedbackQuestionAdmin);

#enable in admin site the following other things
admin.site.register(feedbackQuestionOption);
admin.site.register(feedbackForm,feedbackFormAdmin);
admin.site.register(feedbackAbout);

