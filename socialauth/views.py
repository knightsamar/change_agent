# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect;
from django.contrib.auth.decorators import login_required
from django.template import Context, loader, RequestContext
from django.contrib.auth import logout as auth_logout
from change_agent.settings import MEDIA_URL
from social_auth.backends.google import GoogleOAuth2, GoogleOAuth2Backend

@login_required
def afterglow(request):
    #t = loader.get_template('socialauth/sample.html');
    #c = Context();
    import pdb
    pdb.set_trace()
    #print request.user
    return HttpResponseRedirect("/give_feedback");

def loginHandler(request):
    '''for showing various login options and getting the user to login'''
    next = request.GET.get('next',default='http://google.com/'); #place to where user should be redirected after login
    print "next is ",next;
    t = loader.get_template('socialauth/login_options.html');
    c = Context({
        'next':next,
        'MEDIA_URL':MEDIA_URL,
       });
    return HttpResponse(t.render(c));

def logout(request):
    '''logs you out, duh!'''
    auth_logout(request)
    return HttpResponse("logged - out")
    return HttpResponseRedirect('/')
