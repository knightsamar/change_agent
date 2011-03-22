from django.template import Context, loader
from django.http import HttpResponse
from change_agent.manage_feedback.models import feedbackForm

def index(request):
    form_list = feedbackForm.objects.all()
    t = loader.get_template('give_feedback/index.html');
    c = Context (
	    {
		'form_list' : form_list,
	}) #pass the list to the template
	
    #output = '<h3>List</h3>\n' . join([f.title for f in list_of_forms]); #old line kept here just like that!
    return HttpResponse(t.render(c));

def show_form(request,form):
    f = feedbackForm.objects.get(pk=form);
    t = loader.get_template('give_feedback/form.html');
    c = Context (
           {
             'form' : f
           } );

    return HttpResponse(t.render(c));
