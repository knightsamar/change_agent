from ldap_login.models import *
from ldap_login.views import add_user
import csv;

def importUsers(CSVFile,Newgroup):
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
         
