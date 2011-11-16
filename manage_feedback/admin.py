from manage_feedback.models import feedbackQuestion,feedbackQuestionOption,feedbackForm,feedbackAbout
from django.contrib import admin
from django.template import RequestContext, Context, loader
from ldap_login.models import *
from give_feedback.models import feedbackSubmission
from django.http import HttpResponse
from django.core.context_processors import csrf
from datetime import datetime

#for displaying options directly underneath the question when creating or editing
class feedbackQuestionOptionsInline(admin.TabularInline):
    model = feedbackQuestionOption;
    extra = 4;

class feedbackQuestionAdmin(admin.ModelAdmin):
    inlines = [feedbackQuestionOptionsInline];
    
class feedbackFormAdmin(admin.ModelAdmin):
    actions = ['duplicateForm','notFilled','changeDeadline'];
    list_display=['title', 'deadline_for_filling']
    ordering=['title']
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

    
    def notFilled(self, request, queryset):
        user_dict=dict()
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
                #if f.submitter in user_all:
                user_all.remove(f.submitter)
            user_dict[str(existing_form.title)]=user_all
        t = loader.get_template('manage_feedback/notFilled.html');
        c = Context(
           {
             'forms_users_dict':user_dict
           }
         )
   
        return HttpResponse(t.render(c))
    def changeDeadline(self, request, queryset):
            #it means user has entered the new target deadline
            dd=8            
            mm='Mar'
            yyyy=2011
            #forming the date
            month={'Jan':1, 'Feb':2,'Mar':3, 'April':4,'May':5,'June':6,'July':7,'Aug':8,'Sept':9,'Oct':10,'Nov':11,'Dec':12}
            
            '''dd=int(request.post['date'])
            mm=request.post['month']
            yyyy=int(request.post['year'])'''
            # so for all forms in queryset: 
            for forms in queryset:
                #forms.deadline=request.post['date']
                forms.deadline_for_filling = datetime(yyyy,int(month[mm]),dd);
                forms.save()
           
            #pass    

            '''else:
            t=loader.get_template('manage_feedback/date.html')
            c=RequestContext(request,{});
            return HttpResponse(t.render(c));'''

    duplicateForm.short_description = "Duplicate this form";
    notFilled.short_description = "People who have not filled this form";
    changeDeadline.short_description="Change the deadline";
         
admin.site.register(feedbackQuestion,feedbackQuestionAdmin);

#enable in admin site the following other things
admin.site.register(feedbackQuestionOption);
admin.site.register(feedbackForm,feedbackFormAdmin);
admin.site.register(feedbackAbout);

