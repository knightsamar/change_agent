from django.core.management.base import BaseCommand, CommandError;
from ldap_login.ldapUtils import ldapManager;
from ldap_login.models import user,group;
from datetime import datetime;

class Command(BaseCommand):
    args = None;
    help = "imports LDAP users from Active Directory into database"

    def handle(self, *args, **options):
        #*args is a tuple of positional parameters beyond those defined
        #**options is a dictionary of keyword parameters beyond those defined
        try:
            l = ldapManager();
            groups = l.getGroups()
            for g in groups:
                #does this group exist ?
                try:
                    groupObj = group.objects.get(name=g);
                    print "Using existing group %s" % g
                except group.DoesNotExist:
                    groupObj = group.objects.create(name=g,created_on=datetime.now());
                    groupObj.save();
                    print "Created group %s" % g;
                finally:
                    users = l.getUsers(ou=g,attrs=['sAMAccountName','displayName']);
                    for u in users:
                        print 'Searching for existing user with username : %s ' % u['sAMAccountName'];
                        try:
                            userObj = user.objects.get(pk=u['sAMAccountName'])
                            print "Using existing user %s " % userObj
                        except user.DoesNotExist:
                            userObj = user.objects.create(pk=u['sAMAccountName']);
                            userObj.created_on = datetime.now();
                            userObj.groups.add(groupObj); #add this user to the group;
                            userObj.save();
                            print "Created user %s " % userobj;
                        except Exception as e:
                            print 'An unknown exception occured! ';
                            print e;
