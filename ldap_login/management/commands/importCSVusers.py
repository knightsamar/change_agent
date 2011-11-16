from ldap_login.models import *
from ldap_login.views import add_user
from django.core.management.base import BaseCommand, CommandError;
import csv;

import traceback;
class Command(BaseCommand):
    args = "CSVFile GroupName"
    help = '''
       Imports users from CSV into specified group. 
       If no group is specified, users are simply added. 
       If the group is newer, it will be created.
       You need to specify a CSV file!
    '''
    
    def handle(self, *args, **options):
        if len(args) == 0:
            print self.help;
            return

        CSVFile = args[0];
        Newgroup = args[1];
        if CSVFiles is None:
            print 'You need to specify path to a CSV file!!!'
            return;
        try:
            if Newgroup is None:
                print "No grop specified. just simply adding users";
                g=False;

            else:
                groupexists=group.objects.get_or_create(name=Newgroup)
                g=True;

            handler=csv.reader(open(CSVFile,'rb'),delimiter=',',quotechar=',')
            for row in handler:
                a=row[1].lstrip()[:11];
                print a,".....", a.isdigit();
                newuser=add_user(a);
                if g :
                    
                    newuser.groups.add(groupexists[0]);
                    newuser.save();
        except Exception as e:
            print traceback.print_exc();

