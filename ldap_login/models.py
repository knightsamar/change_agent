from django.db import models
from manage_feedback.models import *;
from give_feedback.models import *
from datetime import datetime
# Create your models here.

class Role(models.Model):
    name = models.CharField(max_length=40,unique=True);
    permissions = models.ManyToManyField('Permission');
    def __str__(self):
        return self.name


class Permission(models.Model):
    name = models.CharField(max_length = 40,unique=True);
    def __str__(self):
        return self.name


#one group has many users
class group(models.Model):
    name = models.CharField(max_length=40,unique=True);
    created_on = models.DateTimeField(auto_now_add=True);
    def set_permission(self,permission):
        for u in self.user_set.all():
            u.role.add(permission);
            
    def getBatch(self):
         print "====",self.name
         Three_yr_courses={ 122:'BBA-IT', 121:'BCA'} 
         Two_yr_courses={ 142:'MSc. (CA)', 141:'MBA-IT'}
         name = self.name
         if self.name.isdigit() is False:
             print "not a digit"
             all_progs = Three_yr_courses.values() + Two_yr_courses.values()
             for k in all_progs:
                if k in self.name:
                    b = self.name[self.name.index(k)+len(k):] # b= batch 2010-12 SA
                    print b
                    print self.name.index(k);
                    name = self.name[self.name.index(k):self.name.index(k)+len(k)]
                    print name;# MSc. (CA)
                    break;
             if name == self.name: #sdrc, staff etc
                print "name was blank"
                programme = self.name
                return self.name
                print "printig after returning"
             else:    #mscca 2010-12 SA
               batch = b.strip()[:7]
               programme = name

         else: # 10030142
            programme=""
            a=0
            try:
                if int(name[5:8]) in Three_yr_courses.keys():
                    a=3
                    programme=Three_yr_courses[int(name[5:8])]
                elif int(name[5:8]) in Two_yr_courses.keys():
                    a=2
                    programme=Two_yr_courses[int(name[5:8])]   
                batch = '20'+str(name[:2]) + '-' + str(a+int(name[:2])) 

            except Exception as e:
                print e;
                programme = self.name;
                batch = None;
       
         return programme,batch;

    def __str__(self):
        if self.name.isdigit() is True:
            try:
                p,b = self.getBatch();
                
                return "%s %s" %(p,b);
            except:
                return self.name
        else:
             return self.name

#many user belongs to one group
class user(models.Model): 
    username = models.CharField(max_length=30,primary_key=True); #without the domain suffix
    password = models.CharField(max_length=255,blank=True,null=True); #we may or many not store the password;
    fullname = models.CharField(max_length=255,blank=True,null=True); #so that we may greet them :D
    last_login = models.DateTimeField(auto_now=True);
    created_on = models.DateTimeField(auto_now_add=True);
    groups = models.ManyToManyField(group);
    allowed_viewing_feedback_about = models.ManyToManyField('manage_feedback.feedbackForm',blank=True,null=True);
    role = models.ForeignKey('Role');

    def has_permission(self,permission_name):
        p = Permission.objects.get_or_create(name = permission_name)[0];
        if p in self.role.permissions.all():
            return True
        else:
            return False;
        
    def __str__(self):
	    return self.username;
    
    def get_unfilled_forms(self):
        all_forms = list(feedbackForm.objects.all().exclude(title="About This Project").filter(deadline_for_filling__gt = datetime.now()).order_by('-deadline_for_filling','about'))
        #print "all-forms.. ", all_forms
        #print "user groups", u.groups.values()
        filled_forms = self.get_filled_forms();
        unfilled_forms=list();
        for g in self.groups.values():
            for f in all_forms:
                if g in f.allowed_groups.values():
                    unfilled_forms.extend([f])
        #print "unfilled forms..!!", unfilled_forms;
        for form in filled_forms:
    	    k = form.feedbackForm
            if k is not None and k in unfilled_forms:
		         unfilled_forms.remove(k)
        return unfilled_forms;

    def get_filled_forms(self):
        feedback_about_list=list()
        feedback_about=self.allowed_viewing_feedback_about.values();
        for a in feedback_about:
            try:
                ab=feedbackForm.objects.get(pk=a['id'])
                #feedback_forms_about=feedbackForm.objects.filter(about=ab)
                feedback_about_list.extend([ab])
            except:
                continue;
        Filled=False
        # to fetch the filled forms for previewing and editing 
    
        filled_forms = list(feedbackSubmission.objects.filter(submitter=self.username));
        return filled_forms;

	
        
