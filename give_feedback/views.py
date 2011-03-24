from django.template import RequestContext, Context, loader
from django.http import HttpResponse
from manage_feedback.models import feedbackForm,feedbackQuestion,feedbackQuestionOption
from django.core.context_processors import csrf

#from accepting submissions;
from give_feedback.models import *;
from ldap_login.models import user;

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
     #submitter = request.SESSION....something
        #find out 
        #who submitted this form? -- will come from the sessions framework
        #was he authorized to submit ? --- validation to be done ...do we store groups and users finally ? how about autocreating them on fetch-from-ldap()?  
    username = 'test';

    s = request.POST; #get the form's submission data
    string = ''

    submission = feedbackSubmission(); #create a new object
    submission.feedbackForm = feedbackForm.objects.get(pk=s['formid']);
    submission.submitter = user.objects.get(username__exact=username);
    submission.save();
    submissionQuestions = dict() #collection of question objects of the questions filled by the user
    submissionAnswers = dict(); #collection of answer objects of the answers given by the user

    for k,v in s.iteritems():
        if k == 'csrfmiddlewaretoken':
            continue; #skip to next iteration...we don't hv anything to do with this
        
        pieces = k.split('_');
        if (pieces[0].contains('q') and len(pieces) = 0):               #this is a question
            submissionQuestions[k] = feedbackQuestion.objects.get(pk=v);
        elif (pieces[0].contains('q') and len(pieces) > 0):             #this is an answer 
            #what type of question is this then ?
            submissionAnswers[k] = feedbackSubmissionAnswer.objects.create();
            if (pieces[1] == 'rdb'):     #this is a radiobutton answer 
                submissionAnswer[k].question = feedbackFormQuestion.objects.get(pk=pieces[0].   

            submissionAnswers[
            #we have answers, store them nicely
    #now for each question answer
    #store the text 
        return HttpResponse("Submitting feedback for %s and request is %s" % (form,s));
  #how many questions ?
 
