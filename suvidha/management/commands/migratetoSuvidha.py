from django.core.management.base import BaseCommand, CommandError
from suvidha.models import User as suvidhaUser 
from suvidha.models import Group as suvidhaGroup

class Command(BaseCommand):
    '''
    This class defines a django management command which provides migration help for migrating Users and Group to 
    Suvidha from any authentication backend that you may be using.

    To know how this works, please read the README.txt
    '''

    can_import_settings = True
    requires_model_validation = True
    help = """Migrates the given model's data to Suvidha User or Group model 

Example:

1) For migrating users:  python manage.py migratetoSuvidha MySpecialAuthApp.models MyUserModel user
2) For migrating groups: python manage.py migratetoSuvidha MySpecialAuthApp.models MyGroupModel group
"""
    args = '<appname.modulename> <modelname> <user/group>'

    def handle(self, *args):
        try:
            if len(args) < 3:
                print self.help
                return

            #this is our source package name
            package = args[0]

            #this is our source model
            model_name = args[1]
            
            #determine what is to be migrated -- user or group ?
            if args[2].lower() == 'users' or args[2].lower() == 'user':
                migrate = 'user'
            elif args[2].lower() == 'groups' or args[2].lower() == 'group':
                migrate = 'group'
            else:
                print "ERROR: You need to specify wheter you are migrating 'user' or 'group'"
                print 
                print self.help
                return 

            #try importing the source model
            print "Checking whether %s.%s is a valid model..." % (package, model_name)

            exec "from %s import %s as source_model" % (package, model_name)
            print 'Importing successfull.'
            print 'Checking for records'
            
            source_records = source_model.objects.all()
            
            if len(source_records) == 0:
				print 'No records found!'
				return
			
            for s in source_records:
                print 'Importing %s...' % (s),
            
                if migrate == 'user':
            	   d = suvidhaUser(userid=s.pk, backend='%s.%s' % (package, model_name))
                elif migrate == 'group':
            	   d = suvidhaGroup(groupid=s.pk, backend='%s.%s' % (package, model_name))
				
                d.save()
                
                print 'Done.'
					
        except CommandError as e:
            print 
            print "Error:", e.message
            print
        except Exception as e:
            print 
            print 'ERROR: ',e.message
            print
