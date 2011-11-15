#comment this line when you ARE OUTSIDE SICSR!
#from ldapAuthBackend import authenticate;
from django.http import HttpResponse;
from django.shortcuts import redirect;
from django.template import RequestContext, loader;
from ldap_login.models import user,group;
from datetime import datetime
from django.core.mail import send_mail

#from django_auth_ldap.config import LDAPSearch
#ldap_login
def login(request):
    #are we processing login attempt ?
    message = None;
    if 'username' in request.session:
        return redirect('/change_agent/give_feedback/');
    if 'username' in request.POST:# and 'password' in request.POST:
        #print 'processing login attempt';
        try:
            #comment this line when you ARE OUTSIDE SICSR!
            status = authenticate(request.POST['username'],request.POST['password']);
            #UNCOMMENT this lin when you are outside SICSR!
            #status = True;
            print status;
            #print 'auth process completed'
        except e as Exception:
            return HttpResponse('Error!!! %s' %  e.message());
        
        if status is True:
            #if successful ldap login
            #update last_login timestamp
            #store encrypted password
            #start session
            request.session['username'] = request.POST['username']; 
            request.session.set_expiry(1800);
            userName=request.session['username']
            #print "because status was", status, "hence message is", message;
    
            #print 'redirecting now...';
	        #check for user existance... and/or add the use in our feedback database..!!
            userexists=user.objects.get_or_create(pk=userName)
            if userexists[1] is True:
                #print " got a new user"
		        # the user not in database... create one..!!
                newuser = userexists[0]
                newuser.username=userName
                newuser.password=''
                newuser.created_on=datetime.today();
                newuser.save();
		        # this auto gruop assignment takes place by the logic that all students log in from thier PRN's and thier 1st 8 digit of thier PRN represents thier gruop.. to assignm a student to another group we need to do it manually..:) and we need to find out a better way of creating groups..!!! :D
		

		    # to check whether its a student or staff.. :)
                if userName.isdigit() is True:
                    #print "its a student"
                    groupid=userName[0:8];
                else:
                    #print "its a staff..!"
                    groupid='staff'
                groupexists=group.objects.get_or_create(name=groupid)
                #print "groupexists... = ", groupexists
            
                # We will have to think of a better method of doing this..!! eventually
                # for SA and SD ppl 
                SA=['009','008','020','025','027','030','031','036','046','048','059','069','076','080','090','093','0100','0101'] # add all the SA ppl ka PRN
                if userName[2:8]=="030142": # if they are in msscca
                    #print "in mscca",userName[2:8]
                    if userName[8:11] in SA: # last three digits of PRN
                        #print "SA- ", userName[8:11]
                        sa=group.objects.get_or_create(name='SA')
                        newuser.groups.add(sa[0])
                    else:
                        #print "SD", userName[8:11]
                        sd=group.objects.get_or_create(name='SD')
                        newuser.groups.add(sd[0])
                newuser.groups.add(groupexists[0]);
                newuser.save();
            else:
                #print "user already existed..!!!"
                userexists[0].last_login=datetime.today();
                userexists[0].save();
             #redirect to the index view!
            return redirect('/change_agent/give_feedback/');
       
        else:#status is false
            message="Incorrect Username Password..!!"
    # #print request.POST['username']
    # #print request.POST['password']
    #print "nothing is  true hence showint the login teplate again"
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
        #print 'logging you out';
		#yes,#then log us out!
        if len(request.session['unfilled']) is not 0:
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

    return redirect('/change_agent/ldap_login/');	

def tester(request):
    return HttpResponse('=====>LOVE YOU DJANGO<======');

