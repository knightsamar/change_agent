from django.template import RequestContext, Context, loader
from django.http import HttpResponse
from manage_feedback.models import feedbackForm,feedbackQuestion,feedbackQuestionOption
from give_feedback.models import feedbackSubmission, feedbackSubmissionAnswer
from django.core.context_processors import csrf

#from accepting submissions;
from give_feedback.models import *;
from ldap_login.models import user;

def index(request):
    username='ldkuser';
    # to fetch the all the forms
    unfilled_forms=feedbackForm.objects.all();
    
    # to fetch the filled forms for previewing and editing 
    filled_forms=feedbackSubmission.objects.filter(submitter=username);

    # to remove the filled forms from the list of all forms to get the newly available forms
    unfilledforms=list(unfilled_forms)
    for form in  filled_forms:
	k=form.feedbackForm
	if (k in unfilledforms):
		unfilledforms.remove(k)
		
	else:
		print "no"
    		
    t = loader.get_template('give_feedback/index.html');
    c = Context (
            {
                'form_list' : filled_forms,
		'unform_list': unfilledforms,
#		'testing':filled_forms
		

        }) #pass the list to the template
 
    #output = '<h3>List</h3>\n' . join([f.title for f in list_of_forms]); #old line kept here just like that!
    return HttpResponse(t.render(c));

def show(request,form):
  
    if ( in )
    #are you allowed to VIEW this feedback form?
    f = feedbackForm.objects.get(pk=form);
    t = loader.get_template('give_feedback/form.html');
    c = RequestContext(request, #we use RequestContext to automagically prevent CSRF
           {
             'form' : f,
           }
        );
    return HttpResponse(t.render(c));

def preview(request,submissionID):
    #ans=feedbackSubmissionAnswer():
    ans=feedbackSubmissionAnswer.objects.filter(submission=submissionID);

    form=feedbackSubmission.objects.get(pk=submissionID).feedbackForm

    t=loader.get_template('give_feedback/preview.html');
    c=RequestContext(request,
	   {
		'answer':ans,
		'form':form
	   }
	);
    return HttpResponse(t.render(c));
    	
#def edit(request,form)
#   ''' handles editing of filled forms.. and updating the tables instead of creating new '''

def submit(request,form):
    '''handles feedback form submission'''
    #submitter = request.SESSION....something
        #find out 
        #who submitted this form? -- will come from the sessions framework
        #was he authorized to submit ? --- validation to be done ...do we store groups and users finally ? how about autocreating them on fetch-from-ldap()?  
    username = 'ldkuser';

    s = request.POST; #get the form's submission data
    string = ''


    submissionObj = feedbackSubmission(); #create a new object
    submissionObj.feedbackForm = feedbackForm.objects.get(pk=s['formid']);
    submissionObj.submitter = user.objects.get(username__exact=username);
    submissionObj.save();

    for k,v in s.iteritems():
        print "i am inside ", s.keys();

        #our form gives us a CSRF token and we don't want to process it here!
        if k == 'csrfmiddlewaretoken':
            continue;   

        pieces = k.split('_');
        print 'pieces are %s ' % pieces;     
        
        #whether this is a field depciting a question simply?
        if ('q' in pieces[0] and len(pieces) == 1):
            if 'M' in v:
                #insert code here to mandatoriness
                v = v.rstrip('M');

        elif ('q' in pieces[0] and len(pieces) > 1):
            print 'pieces are ',pieces;

            if (pieces[1] == 'rdb'):
                #construct an answer object
                submissionAnswerObj = feedbackSubmissionAnswer(
                    question = feedbackQuestion.objects.get(pk=int(pieces[0].lstrip('q'))),
                    answer_option = feedbackQuestionOption.objects.get(pk=v),
                    submission = submissionObj
                )
            elif (pieces[1] == 'chk'):
                print 'got a checkbox!';
                submissionAnswerObj = feedbackSubmissionAnswer(
                    question = feedbackQuestion.objects.get(pk=int(pieces[0].lstrip('q'))),
                    answer_option = feedbackQuestionOption.objects.get(pk=int(pieces[2].lstrip('opt'))),
                    submission = submissionObj
                )
            elif (pieces[1] == 'txt'):
                print 'got a textbox'
                submissionAnswerObj = feedbackSubmissionAnswer(
                    question = feedbackQuestion.objects.get(pk=int(pieces[0].lstrip('q'))),
                    answer_text = v,
                    submission = submissionObj
                )

            submissionAnswerObj.save(); #save this answer!

            t = loader.get_template('give_feedback/submit.html');
            c = RequestContext(request,
             {
                    'submissionID' : submissionObj.id,
             }
           );

    return HttpResponse(t.render(c));

