from django.db import models

# Create your models here.
class user(models.Model): 
	username = models.CharField(max_length=30,primary_key=True); #without the domain suffix
	password = models.CharFiled(max_length=255,blank=True,null=True); #we may or many not store the password;
	last_login = models.DateTimeField(auto_now=True);

	
