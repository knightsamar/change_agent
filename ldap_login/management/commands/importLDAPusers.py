from django.core.management.base import NoArgsCommand, CommandError;
from ldap_login.ldapUtils import ldapManager;
from ldap_login.models import user,group,Role;
from datetime import datetime;
import traceback;

class Command(NoArgsCommand):
    """Import LDAP users from Active Directory.
       Uses the ldapUtils backend.
       Creates the users in our databases else uses existings users.
       Updates group bindings and full names for existing and new users also.
    """
    args = None;
    help = "imports LDAP users from Active Directory into database"
    can_import_settings = True
  
    exclusion_list = ['exam','Domain Controllers']; #list of OUs we do not want to handle at all.
    def handle_noargs(self,  **options):
        #**options is a dictionary of keyword parameters beyond those defined
        try:
            l = ldapManager();
            groups = l.getGroups()
            for g in groups:
                if g in self.exclusion_list :
                    continue; 

                print "-" * 60
                print '\nProcessing group %s' % g;
                #does this group exist in our database ?
                try:
                    groupObj = group.objects.get(name=g);
                    print "Using existing group %s" % g
                except group.DoesNotExist:
                    groupObj = group(name=g,created_on=datetime.now());
                    groupObj.save();
                    print "Created group %s" % g;
                finally:
                    users = l.getUsers(ou=g,attrs=['sAMAccountName','displayName']);
                    for u in users:
                        print "-" * 20
                        username = u['sAMAccountName'][0]; #because we get a dictionary of lists from ldap!
                        print '\nSearching for existing user with username : %s ' % username;
                        try:
                            userObj = user.objects.get(pk=username)
                            print "Using existing user %s " % userObj
                        except user.DoesNotExist:
                            userObj = user(pk=username);
                            userObj.created_on = datetime.now();
                            print "Created user %s " % userObj;
                        except Exception as e:
                            print 'An unknown exception occured! ';
                            print e;
                            print traceback.print_exc();
                        finally: #so that we update these properties for all user
                            if 'displayName' in u:
                                userObj.fullname = u['displayName'][0] #because it's a dictionary of lists!
			    else:
                                userObj.fullname = userObj.pk
			    #Don't forget to assign role!
		            if username.startswith('0') or username.startswith('1'):
				userObj.role = Role.objects.get_or_create(name='student')[0]
			    else:
				userObj.role = Role.objects.get_or_create(name='faculty')[0]

                            userObj.save();
			    #the following must be done after saving 
			    #refer: http://stackoverflow.com/questions/7837033/valueerror-cannot-add-instance-is-on-database-default-value-is-on-databas
                            userObj.groups.add(groupObj); #add this user to the group;
        except KeyError as e:
            print 'KeyError happened in the structure :'
            print e.message
            print 'Structure:', u
            print
        except Exception as e:
            print 'Some unexpected exception occured!';
            print e;
            print traceback.print_exc()
            
