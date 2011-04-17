from django.template import RequestContext, Context, loader
from django.http import HttpResponse,HttpResponseNotFound
from manage_feedback.models import feedbackForm,feedbackQuestion,feedbackQuestionOption
from give_feedback.models import feedbackSubmission, feedbackSubmissionAnswer
from django.core.context_processors import csrf

#from accepting submissions;
from give_feedback.models import *;
from ldap_login.models import user;

#for date
from datetime import *

def hamari404():
    #for customizing our 404
    return HttpResponseNotFound('<h2>Not found!</h2>');

def index(request):
    """for rendering the index page for any user who has just logged in"""
    username='ldkuser';
    # to fetch the all the forms
    unfilled_forms=feedbackForm.objects.all();
    
    # to fetch the filled forms for previewing and editing 
    filled_forms=feedbackSubmission.objects.filter(submitter=username);

    # to remove the filled forms from the list of all forms to get the newly available forms
    unfilledforms=list(unfilled_forms)
    for form in filled_forms:
    	k=form.feedbackForm
	
    if (k in unfilledforms):
		unfilledforms.remove(k)

    d=datetime.today();
    		
    t = loader.get_template('give_feedback/index.html');
    c = Context (
            {
                'form_list' : filled_forms,
		        'unform_list': unfilledforms,
#		        'testing':filled_forms,
                'today' : d
            }  ) #pass the list to the template
 
    #output = '<h3>List</h3>\n' . join([f.title for f in list_of_forms]); #old line kept here just like that!
    return HttpResponse(t.render(c));

def show(request,form):
    '''show feedback form FOR the FIRST TIME so that user can edit it'''     
    #are you allowed to VIEW this feedback form?

    # is the deadline exceded??
    now = datetime.today()
    f = feedbackForm.objects.get(pk=form); 
    mandatoryQuestions = f.mandatoryQuestions();
    if (f.deadline_for_filling < now ):
        print "lalala"
        return HttpResponse("Sorry deadline exceedd..:)");
    else:
        flag='show'
        t = loader.get_template('give_feedback/form.html');
        c = RequestContext(request, #we use RequestContext to automagically prevent CSRF
           {
             'form' : f,
             'flag':flag,
             'mandatoryQuestions':mandatoryQuestions,
           }
         );
        return HttpResponse(t.render(c));

def preview(request,submissionID):
    if submissionID is None:
        return hamari404();
        
    ans=feedbackSubmissionAnswer.objects.filter(submission=submissionID);
    #submissionID=0 #why do we need to set submissionID to 0 ? 

    if ans is None:
        return hamari404();

    form=feedbackSubmission.objects.get(pk=submissionID).feedbackForm
    now=datetime.today();
    t=loader.get_template('give_feedback/preview.html');
    c=RequestContext(request,
	   {
		'answer':ans,
		'form':form,
        'submissionID':submissionID,
        'date':now
	   }
	);
    return HttpResponse(t.render(c));
    	
    submissionID=0
def edit(request):
    #handles editing of filled forms.. and updating the tables instead of creating new 
    if (request.POST):
        s = request.POST;
        submissionID = s['submissionID']
    else:
        #no submission id was passed for editing!
        return hamari404();
    
    now=datetime.today()
    ans=feedbackSubmissionAnswer.objects.filter(submission=submissionID);
    form=feedbackSubmission.objects.get(pk=submissionID).feedbackForm
    mandatoryQuestions = form.mandatoryQuestions();
    #have we exceeded the deadline already ???
    if (form.deadline_for_filling < now ):
        return HttpResponse("Sorry deadline exceedd..:)");
    else:
        flag='edit'
        t = loader.get_template('give_feedback/form.html');
        c = RequestContext(request, #we use RequestContext to automagically prevent CSRF
           {
             'form' : form,
             'flag':flag,
             'answer':ans,
             'submissionID':submissionID,
             'mandatoryQuestions':mandatoryQuestions

           }
         );

    return HttpResponse(t.render(c));
       
def editsubmit(request,form):
    #handles feedback form submission
    #submitter = request.SESSION....something
        #find out 
        #who submitted this form? -- will come from the sessions framework
        #was he authorized to submit ? --- validation to be done ...do we store groups and users finally ? how about autocreating them on fetch-from-ldap()?  
    username = 'ldkuser';

    s = request.POST; #get the form's submission data
    string = ''
    now=datetime.today()
    

    submissionObj = feedbackSubmission.objects.get(pk=s['submissionID']); #create a new objecisting answer object
    #submissionObj.feedbackForm = feedbackForm.objects.get(pk=s['formid']);
    #submissionObj.submitter = user.objects.get(username__exact=username);
    submissionObj.when=now;
    submissionObj.save();

    for k,v in s.items():
        #our form gives us a CSRF token and we don't want to process it here!
        if k == 'csrfmiddlewaretoken':
            continue;   
        if k == s['submissionID']:
            continue;
        pieces = k.split('_');
        #whether this is a field depciting a question simply?
        #if ('q' in pieces[0] and len(pieces) == 1):
        #    if 'M' in v:
        #        #insert code here to mandatoriness
        #        v = v.rstrip('M');
        if ('q' in pieces[0] and len(pieces) > 1):
            if (pieces[1] == 'rdb'):
                #construct an answer object
                q = feedbackQuestion.objects.get(pk=int(pieces[0].lstrip('q')))
                submissionAnswerObj = feedbackSubmissionAnswer.objects.filter(question=q).filter(submission=submissionObj)[0]
                submissionAnswerObj.answer_option = feedbackQuestionOption.objects.get(pk=v)
            elif (pieces[1] == 'chk'):
                 submissionAnswerObj = feedbackSubmissionAnswer.objects.filter(question=q).filter(submission=submissionObj)[0]
                 submissionAnswerObj.answer_option = feedbackQuestionOption.objects.get(pk=int(pieces[2].lstrip('opt')))
            elif (pieces[1] == 'txt'):
                 print 'got a textbox'
                 q =  feedbackQuestion.objects.get(pk=int(pieces[0].lstrip('q')))
                 submissionAnswerObj = feedbackSubmissionAnswer.objects.filter(question=q).filter(submission=submissionObj)[0]
                 submissionAnswerObj.answer_text = v
            submissionAnswerObj.save(); #save this answer!
        t = loader.get_template('give_feedback/submit.html');
        c = RequestContext(request,
             {
                    'submissionID' : submissionObj.id,
             }
           );
    return HttpResponse(t.render(c));


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
        #our form gives us a CSRF token and we don't want to process it here!
        if k == 'csrfmiddlewaretoken':
            continue;   

        pieces = k.split('_');

        
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

