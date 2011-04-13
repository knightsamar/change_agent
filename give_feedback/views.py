from django.template import RequestContext, Context, loader
from django.http import HttpResponse
from manage_feedback.models import feedbackForm,feedbackQuestion,feedbackQuestionOption
from give_feedback.models import feedbackSubmission, feedbackSubmissionAnswer
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

def preview(request,submissionID):
    #ans=feedbackSubmissionAnswer():
    ans=feedbackSubmissionAnswer.objects.filter(submission=submissionID);
    t=loader.get_template('give_feedback/preview.html');
    c=RequestContext(request,
	   {
		'answer':ans
	   }
	);
    return HttpResponse(t.render(c));
    	
    '''handles submitted form preview..!
     #submitter = request.SESSION....something
        #find out 
        #who submitted this form? -- will come from the sessions framework
        #was he authorized to submit ? --- validation to be done ...do we store groups and users finally ? how about autocreating them on fetch-from-ldap()?  
    username = 'ldkuser';
    #submission = Submission(); #create a new object
    submission.feedbackForm = feedbackForm.objects.get(pk=s['formid']);
    submission.submitter = user.objects.get(username__exact=username);
    submission.save();
    submissionQuestion = dict() #collection of question objects of the questions filled by the user
    submissionAnswer = dict(); #collection of answer objects of the answers given by the user

    for k,v in s.iteritems():
        if k == 'csrfmiddlewaretoken':
            continue; #skip to next iteration...we don't hv anything to do with this
        
        pieces = k.split('_');
        print pieces;
        print "type is ", type(pieces[0]);
        if ('q' in pieces[0] and len(pieces) == 1):               #this is a question
            if 'M' in v:
                #insert code here to check the mandatoriness of the answers's submission
                
                #now remove the M
                v = v.rstrip('M');
            submissionQuestion[k] = feedbackQuestion.objects.get(pk=v);
            #to be used for mandatory processing.
        elif ('q' in pieces[0]  and len(pieces) > 1):             #this is an answer 
            #what type of question is this then ?
            print "pieces are ",pieces
            #we have answers, store them nicely
                
            if (pieces[1] == 'rdb'):     #this is a radiobutton answer 
                submissionAnswer[k] = feedbackSubmissionAnswer(
                    question = feedbackQuestion.objects.get(pk=int(pieces[0].lstrip('q'))),
                    answer_option = feedbackQuestionOption.objects.get(pk=v), #because radio buttons groups are namedin a bunch with one name and their values differ.
                    submission = submission,
                    )
            elif (pieces[1] == 'chk'):  #this is a checkbox wala answer;
                submissionAnswer[k] = feedbackSubmissionAnswer(
                    question = feedbackQuestion.objects.get(pk=int(pieces[0].lstrip('q'))),
                    answer_option = feedbackQuestionOption.objects.get(pk=int(pieces[2].lstrip('opt'))), #because check boxes are named seperately.
                    submission = submission,
                    )
            elif (pieces[1] == 'txt'):  #this is a txt wala answer;
                submissionAnswer[k] = feedbackSubmissionAnswer(
                    question = feedbackQuestion.objects.get(pk=int(pieces[0].lstrip('q'))),
                    answer_text = v,
                    submission = submission,
                    )
        
        t = loader.get_template('give_feedback/submit.html');
        c = RequestContext(request, #we use RequestContext to automatically prevent CSRF
           {
             'submission' : submission,
           }
        );
        submission.save();
    return HttpResponse(t.render(c));'''
    #return HttpResponse("submission id %s  answer option %s" % (submissionID, ans[0].answer_option));

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

