from django.template import RequestContext, Context, loader
from django.http import HttpResponse
from change_agent.manage_feedback.models import feedbackForm
from django.core.context_processors import csrf

def index(request):
    form_list = feedbackForm.objects.all()
    t = loader.get_template('give_feedback/index.html');
    c = Context (
	    {
		'form_list' : form_list,
	}) #pass the list to the template
 
    #output = '<h3>List</h3>\n' . join([f.title for f in list_of_forms]); #old line kept here just like that!
    return HttpResponse(t.render(c));

def show(request,form):
    #are you allowed to VIEW this feedback form?
    f = feedbackForm.objects.get(pk=form);
    t = loader.get_template('give_feedback/form.html');
    c = RequestContext(request, #we use RequestContext to automagically prevent CSRF
           {
             'form' : f,
           }
        );
    return HttpResponse(t.render(c));

def submit(request,form):
    '''handles feedback form submission'''
    #find out
        #who submitted this form? -- will come from the sessions framework
        #was he authorized to submit ? --- validation to be done ...do we store groups and users finally ? how about autocreating them on fetch-from-ldap()?

        #how many questions ?
        #now for each question answer
            #store the text 
    
    c = request.POST;

    return HttpResponse("Submitting feedback for %s and request is %s" % (form,c.items()));

