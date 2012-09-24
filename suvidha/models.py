from django.db import models
class User(models.Model):
	recordid = models.AutoField(primary_key = True)
	userid = models.CharField(max_length=100,blank=False,null=False, 
verbose_name = "User ID in the actual backend, MUST be a primary key")
	backend = models.CharField(max_length=100, blank=False, null=False, verbose_name="user backend", help_text="The user backend in the form APP_NAME.MODELS_FILE.MODEL_NAME")
	
	def __str__(self):
		return "%s user from %s" % (self.userid, self.backend)	
	
	def get_real_user(self):
		print 'Accessing', self.backend
		try:
			backend_split = self.backend.split('.')
			#construct the module_name someapp.somemodule.
			module_name = ('.').join(backend_split[0:-1])
			#get the modelname -- the name at the end of the backend
			model_name = backend_split[-1]
			exec "from %s import %s as backend_model" % (module_name, model_name)
			return backend_model.objects.get(pk=self.userid)
		except ImportError as e:
			print "Error while accessing the real user %s in the backend %s" % (self.userid, self.backend)
			print "Exception: ", e.message;
			return None
		except Exception as e:
			print "Exception: ", e.message;
			return None;

class Group(models.Model):
	recordid=models.AutoField(primary_key=True)
	groupid=models.CharField(max_length=100, blank=False, null=False, 
verbose_name="Group ID in the actual backend")
	backend=models.CharField(max_length=100, blank=False, null=False, verbose_name = "group backend")

	def __str__(self):
		return "%s group from %s" % (self.groupid,self.backend)
		
		
	def get_real_group(self):
		print 'Accessing', self.backend
		try:
			backend_split = self.backend.split('.')
			#construct the module_name someapp.somemodule.
			module_name = ('.').join(backend_split[0:-1])
			#get the modelname -- the name at the end of the backend
			model_name = backend_split[-1]
			exec "from %s import %s as backend_model" % (module_name, model_name)
			return backend_model.objects.get(pk=self.groupid)
		except ImportError as e:
			print "Error while accessing the real group %s in the backend %s" % (self.groupid, self.backend)
			print "Exception: ", e.message;
			return None
		except Exception as e:
			print "Exception: ", e.message;
			return None;