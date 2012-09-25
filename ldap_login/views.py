#comment this line when you ARE OUTSIDE SICSR!
from change_agent.settings import ROOT
if ROOT !="":
    from ldapAuthBackend import authenticate;
from django.http import HttpResponse;
from django.shortcuts import redirect, render_to_response;
from django.template import RequestContext, loader;
from ldap_login.models import user,group,Role;
from datetime import datetime
from django.core.mail import send_mail
from django.views.decorators.cache import cache_page


#from django_auth_ldap.config import LDAPSearch
#ldap_login
def login(request):
    #are we processing login attempt ?
    message = None;
    if 'username' in request.session:
        if 'redirect' in request.session:
            return redirect(request.session['redirect']);
        else:
            return redirect('%s/give_feedback/'%ROOT);
            
    if 'username' in request.POST:# and 'password' in request.POST:
        #print 'processing login attempt';
        try:
            #comment this line when you ARE OUTSIDE SICSR!
            if ROOT != "":
                status = authenticate(request.POST['username'],request.POST['password']);
            else:
                #UNCOMMENT this lin when you are outside SICSR!
                status = True;
            print ROOT,status;
            #print 'auth process completed'
        except Exception as e:
            return HttpResponse('Error!!! %s' % e.message);
        
        if status is True:
            #if successful ldap login
            #update last_login timestamp
            #store encrypted password
            #start session
            request.session['username'] = request.POST['username']; 
            userName=request.session['username']
            request.session.set_expiry(1800)
            add_user(userName);		
            print 'redirecting now...';
	    print ROOT;
            if 'redirect' in request.session:
                return redirect(request.session['redirect'])
            else:    
                return redirect('%s/give_feedback/'%ROOT);
        else:
            message = 'Wrong Username/password';
            print "because status was", status, "hence message is", message;
            #print "because status was", status, "hence message is", message;
       
    # #print request.POST['username']
    # #print request.POST['password']
    print "nothing is  true hence showint the login teplate again"
    #we aren't either procesing a login attempt OR the user had a failed login attempt!
    t = loader.get_template('ldap_login/login.html');
    c = RequestContext (request,
        {
          'message' : message,
          'ROOT':ROOT
        });
         
    return HttpResponse(t.render(c));
          
        
    #unsuccessful ldap login
    #wrong username/password!!!

def add_user(prn):
        r = Role.objects.get_or_create(name = 'student')
        r[0].save();
        try:
            print "user already existed..!!!"
            userexists=user.objects.get(pk=prn)
            userexists.last_login=datetime.today();
            userexists.save();
            return userexists; 
        except:
            print " got a new user"
		    # the user not in database... create one..!!
            newuser = user(
                        username=prn,
                        password = '',
                        created_on=datetime.today(),
                        role = r[0],
                    );
            newuser.save();
		    # this auto gruop assignment takes place by the logic that all students log in from thier PRN's and thier 1st 8 digit of thier PRN represents thier gruop.. to assignm a student to another group we need to do it manually..:) and we need to find out a better way of creating groups..!!! :D
		

		    # to check whether its a student or staff.. :)
            if prn.isdigit() is True:
                print "its a student"
                groupid=prn[0:8];
            else:
                print "its a staff..!"
                groupid='staff'
            groupexists=group.objects.get_or_create(name=groupid)
            print "groupexists... = ", groupexists
            newuser.groups.add(groupexists[0]);
            newuser.save();
            return newuser; 
        

def logout(request):
    #are we actually logged in ?
    if 'username' in request.session:
        #print 'logging you out';
		#yes,#then log us out!
        if 'unfilled' in request.session and len(request.session['unfilled']) is not 0:
            # the person has unfillwd forms
            emailid=request.session['username']+"@sicsr.ac.in"
            emailid=[emailid,];
            print "Sending mail to ",emailid
            send_mail("Feedback Forms - Unfilled!", "You have unfilled forms left. Please fill them before the deadline!","root@sdrcserver.sdrc", emailid,fail_silently=True);
        request.session.flush();
    #else:
		#no,
        #print 'redirecting to login page to tell you to login first :P';
			#then tell me to login first, using the message if possible 
			#message = "Hey, you need to go in before you can go out :P :P";

    return redirect('%s/ldap_login/'%ROOT);	

#cache this view's output for 6 hrs, needs to be specified in seconds
@cache_page(6 * 60 * 60)
def passwordHelp(request):
    if 'username' in request.session:
        return redirect('%s/give_feedback/'%ROOT);
    else:
        return render_to_response('ldap_login/passwordhelp.html');
     
def tester(request):
    return HttpResponse('=====>LOVE YOU DJANGO<======');

