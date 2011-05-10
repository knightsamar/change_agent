from django.db import models
# Create your models here.

#one group has many users
class group(models.Model):
    name = models.CharField(max_length=20,unique=True);
    created_on = models.DateTimeField(auto_now_add=True);

    def __str__(self):
	return self.name;

#many user belongs to one group
class user(models.Model): 
    username = models.CharField(max_length=30,primary_key=True); #without the domain suffix
    password = models.CharField(max_length=255,blank=True,null=True); #we may or many not store the password;
    last_login = models.DateTimeField(auto_now=True);
    created_on = models.DateTimeField(auto_now_add=True);
    groups = models.ManyToManyField(group);
    allowed_viewing_feedback_about = models.ManyToManyField('manage_feedback.feedbackAbout',blank=True,null=True);

    def __str__(self):
	return self.username;


