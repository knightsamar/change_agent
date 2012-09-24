#from suvidha.models import User,Group
def migrate(self):
	for o in old_users:
    		u = User(userid=o.username, backend='ldap_login.models.user') 
    		u.save() #used to migrate ldap_login.models.user
	

