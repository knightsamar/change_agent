# Create your views here.
from ldapAuthBackend import authenticate;
from django.http import HttpResponse;
from django.shortcuts import redirect;
from django.template import RequestContext, loader;

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
        	print 'auth successfull!'
        except e as Exception:
            return HttpResponse('Error!!! %s' %  e.message());
            
        if status is True:
            #if successful ldap login
            #update last_login timestamp
            #store encrypted password
            #start session
            request.session['username'] = request.POST['username']; 
            print 'redirecting now...';
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
 
