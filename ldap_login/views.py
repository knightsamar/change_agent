# Create your views here.
from ldapAuthBackend import authenticate;
from django.http import HttpResponseRedirect;
from django.template import RequestContext, Context, loader;

#from django_auth_ldap.config import LDAPSearch
#ldap_login
def login(request):
	#are we processing login attempt ?
        message = None;
        if 'username' in request.POST and 'password' in request.POST:
            print 'processing login attempt';
            try:
                status = authenticate(request.POST['username'],request.POST['password']);
                #for now all auths are true :*
                status = True;
            except e as Exception:
                return HttpResponse('Error!!! %s' %  e.message());
            
            if status is True:
                 #if successful ldap login
		         #update last_login
                 #store encrypted password
	    	     #start session
                 request.session['username'] = request.POST['username']; 

                return HttpResponseRedirect('/give_feedback/');              
                #redirect to the index view!
            else:
                message = 'Wrong Username/password';

         #we aren't either procesing a login attempt OR the user had a failed login attempt!
         t = loader.get_template('ldap_login/login.html');
         c = Context (
            {
                'message' : message
            });
         return HttpResponse(t.render(c));
          
        
		#unsuccessful ldap login
		#wrong username/password!!!
 
