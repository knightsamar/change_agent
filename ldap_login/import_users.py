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
        print row[1][:11];
        newuser=add_user(row[1][:11]);
        if(g):
            newuser.groups.add(groupexists[0]);
            newuser.save();
         



