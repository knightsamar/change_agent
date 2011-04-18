# Create your views here.
from ldapAuthBackend import authenticate;
from django.http import HttpResponse;
from django.shortcuts import redirect;
from django.template import RequestContext, loader;
from ldap_login.models import user,group;
from datetime import datetime

#from django_auth_ldap.config import LDAPSearch
#ldap_login
def login(request):
    #are we processing login attempt ?
    message = None;
    if 'username' in request.session:
        return redirect('/give_feedback');
    if 'username' in request.POST and 'password' in request.POST:
        print 'processing login attempt';
        try:
        	status = authenticate(request.POST['username'],request.POST['password']);
        	#for now all auths are true :*
        	#status = True;
        	print status;
        	print 'auth process completed'
        except e as Exception:
            return HttpResponse('Error!!! %s' %  e.message());
            
        if status is True:
            #if successful ldap login
            #update last_login timestamp
            #store encrypted password
            #start session
            request.session['username'] = request.POST['username']; 
            userName=request.session['username']
	    print userName
            print 'redirecting now...';
	    #check for user existance... and/or add the use in our feedback database..!!
	    userexists=user.objects.get_or_create(pk=userName)
            if userexists[1] is True:
		# the user not in database... create one..!!
		newuser=userexists[0]
		newuser.username=userName
		newuser.password=''
		newuser.created_on=datetime.today();
		newuser.save();
		# this auto gruop assignment takes place by the logic that all students log in from thier PRN's and thier 1st 8 digit of thier PRN represents thier gruop.. to assignm a student to another group we need to do it manually..:) and we need to find out a better way of creating groups..!!! :D
		

		# to check whether its a student or staff.. :)
		if userName.isdigit() is True:
			groupid=userName[0:8];
		else:
			groupid='staff'
		groupexists=group.objects.get_or_create(name=groupid)

		newuser.group=groupexists[0];
		newuser.save();
  	    else:
		print "user already existed..!!!"
		userexists[0].last_login=datetime.today();
		userexists[0].save();
		
            #redirect to the index view!
            return redirect('/give_feedback/');
        else:
            message = 'Wrong Username/password';
            print "because status was", status, "hence message is", message;
    
   # else:
   
    # print request.POST['username']
    # print request.POST['password']
    print "nothing is  true hence showint the login teplate again"
    #we aren't either procesing a login attempt OR the user had a failed login attempt!
    t = loader.get_template('ldap_login/login.html');
    c = RequestContext (request,
        {
          'message' : message
        });
         
    return HttpResponse(t.render(c));
          
        
    #unsuccessful ldap login
    #wrong username/password!!!

def logout(request):
	#are we actually logged in ?
	if 'username' in request.session:
		print 'logging you out';
		#yes,#then log us out!
		request.session.flush();
	else:
		#no,
		print 'redirecting to login page to tell you to login first :P';
			#then tell me to login first, using the message if possible 
			#message = "Hey, you need to go in before you can go out :P :P";

	return redirect('/change_agent/');	
