from django.template import RequestContext, Context, loader
from django.http import HttpResponse,HttpResponseNotFound
from django.shortcuts import redirect
from manage_feedback.models import feedbackForm,feedbackQuestion,feedbackQuestionOption, feedbackAbout, Batch, Subject
from give_feedback.models import feedbackSubmission, feedbackSubmissionAnswer
from django.core.context_processors import csrf
#from accepting submissions;
from give_feedback.models import *;
from ldap_login.models import user,group;
from change_agent.settings   import ROOT, CREATEFORMS
#for date
from datetime import datetime

def hamari404():
    #for customizing our 404
    return HttpResponseNotFound('<h2>Not found!</h2>');

def index(request):
    """for rendering the index page for any user who has just logged in"""
    print "first line" 
    if 'username' not in request.session or request.session['username'] == None:
        print "not logged in"
        return redirect('%s/ldap_login/'%ROOT);
    else:
        print 'username in session object';
        username = request.session['username'];
        u=user.objects.get(pk=username)
    
    try:
        about_us=feedbackForm.objects.get(title="About This Project") 
    except:
        print "create the about us form...;)"
        about_us = ""
        Filled = True;
    def form(f):
        try:
            return f.feedbackForm;
        except:
            pass;

    if about_us in map(form,u.feedbacksubmission_set.all()):
        Filled = True;
    else:
        Filled  = False;
    #TO ADD:- check for group as staff... not that important...:) 
    #print request.session['unfilled']            
    # for displaying date and checking for deadline
    d = datetime.today();
    n = datetime.now()		

    t = loader.get_template('give_feedback/index.html');
    c = RequestContext (request,
            {
                'user' : u,
                'unfilled_forms':u.get_unfilled_forms(),
                'filled_forms':u.get_filled_forms(),
                'admin':u.has_permission('admin'),
                'feedback_about':u.allowed_viewing_feedback_about.all(),
	        	'About_us_filled' : Filled,'view_forms':u.has_permission('view forms'),
                 'fill_forms':u.has_permission('fill forms'),
                'today' : d,
                'rightnow' : n, #because template api already has tag called now
                'ROOT':ROOT,
            }  ) #pass the list to the template
 
    return HttpResponse(t.render(c));

     
def show(request,form):
    '''show feedback form FOR the FIRST TIME so that user can edit it'''     
    #are you allowed to VIEW this feedback form?

    #user is not logged in 
    if 'username' not in request.session or request.session['username'] == None: 
        request.session['redirect'] = request.get_full_path()
        return redirect('/change_agent/ldap_login/'); 
    else: #is logged in!
	# username = str(request.session['username']);
	#Kannan just added the next 2 lines replacing the above line
	username = request.session['username'];
        u=user.objects.get(pk=username)
       
    #for feedback Forms Filling   
    f = feedbackForm.objects.get(pk=form);
    # is this form actually unfilled??

    print 'I am in show and f is %s' % (f);
    #print 'and unfilled is %s' % (request.session['unfilled']);

    if 'unfilled' in request.session and f not in request.session['unfilled']:
        return redirect('%s/manage_feedback/1/error'%ROOT);
    mandatoryQuestions = f.mandatoryQuestions();

    # is the deadline exceded??
    now = datetime.today()
    print u.has_permission('fill forms')
    
    if (f.deadline_for_filling < now ):
        return redirect("%s/manage_feedback/2/error"%ROOT);
    else:
        flag='show'
        t = loader.get_template('give_feedback/form.html');
        c = RequestContext(request, #we use RequestContext to automagically prevent CSRF
           {
             'username': username,
             'form' : f,
             'flag' : flag,
             'ROOT':ROOT,
             'mandatoryQuestions':mandatoryQuestions,
           }
         );
        return HttpResponse(t.render(c));

def preview(request,submissionID):
    if 'username' not in request.session or request.session['username'] == None:
        request.session['redirect'] = request.get_full_path()
        return redirect('%s/ldap_login/'%ROOT);
    else:
        username = str(request.session['username']);

    print "the username in preview is : ", username;

    if submissionID is None:
        return hamari404();
          
    ans = feedbackSubmissionAnswer.objects.filter(submission=submissionID).extra(order_by = ['question']); #so that we can group
    ans_dict = ans.values()
    print "--> We have ", ans; 
    #submissionID=0 #why do we need to set submissionID to 0 ? 

    if ans is None:
        return hamari404();

    f = feedbackSubmission.objects.get(pk=submissionID)
    form = f.feedbackForm
   
    # whether this  form submission is actually owned by the user...
    Submitter = str(f.submitter)
    if Submitter != username:
    	return redirect("%s/manage_feedback/3/error"%ROOT)#"boohoooooooooo..!! caught ya..!!! ")

    now = datetime.today();
    #print "filled forms as per preview...", request.session['filled'];
    nextform = None 
    #preview function also allows navigation to next preview
    if 'filled' in request.session:
        if len(request.session['filled']) is 0:
            nextform = None;
        else:    
            nextform = request.session['filled'][0];

        if f in request.session['filled']:
            index = request.session['filled'].index(f) + 1
            if len(request.session['filled']) > index:
                nextform = request.session['filled'][index]
            else:
                nextform = None
                print "next from",nextform,"type",type(nextform)
        else:
            	print "this form",form," not in filled form"

    #make a good list to print questions and their selected answers
    #get all the answers given by the user in the submission object.
    answers = feedbackSubmissionAnswer.objects.filter(submission=submissionID).order_by('question'); 
    #create a blank dictionary:
    submissionDetails = [];
    #for each answer
    for a in answers:
        if  a.answer_text is None: 
            d = {'question' : a.question.text, 'answer' : a.answer_option.text };
            #insert into the list
            submissionDetails.append(d);
            #question text
            #question answer value.
        else:
            d = {'question' : a.question.text, 'answer' : a.answer_text };
            submissionDetails.append(d);

    t = loader.get_template('give_feedback/preview.html');
    c = RequestContext(request,
	    {
		'answer':ans,
		'form':form,
      	'submissionID':submissionID,
       	'date':now,
		'sub':Submitter,
		'username':username,
		'nextform':nextform,
        'submissionDetails':submissionDetails,
        'ROOT':ROOT
        }
	);
    return HttpResponse(t.render(c));
    	
def edit(request):
    #handles editing of filled forms.. and updating the tables instead of creating new 
    # if the user is lot logged in.. redirect to login page

    if 'username' not in request.session or request.session['username'] == None:
        request.session['redirect'] = request.get_full_path()
        return redirect('%s/ldap_login/'%ROOT);
    else:
        username = str(request.session['username']);
    
    # getting the submissionID from the post
    if (request.POST):
        s = request.POST;
        submissionID = s['submissionID']
    else:
        #no submission id was passed for editing!
        return hamari404();
    
    Submitter = str(feedbackSubmission.objects.get(pk=submissionID).submitter)
    print 'S=', type(Submitter),"U=",type(username)
    
    #every user is allowed to edit only 
    if Submitter != username:
    	return redirect("%s/manage_feedback/3/error"%ROOT); 
    
    now = datetime.today()
    ans = feedbackSubmissionAnswer.objects.filter(submission=submissionID);
    form = feedbackSubmission.objects.get(pk=submissionID).feedbackForm
   
    mandatoryQuestions = form.mandatoryQuestions();
    
    #have we exceeded the deadline already ???
    if (form.deadline_for_filling < now ):
        return redirect("%s/manage_feedback/2/error"%ROOT);
    else:
        flag='edit' #so that we can render the same template for editing as well as filling new forms.
	
        t = loader.get_template('give_feedback/form.html');
        c = RequestContext(request, #we use RequestContext to automagically prevent CSRF
           {
             'form' : form,
             'flag' : flag,
             'answer':ans,
             'submissionID':submissionID,
             'mandatoryQuestions':mandatoryQuestions,
    	     'username':username,
             'ROOT':ROOT
           }
         );

    return HttpResponse(t.render(c));
       
def editsubmit(request,form):
    """handles feedback form submission from EDITs"""

    #are we logged in ?
    if 'username' not in request.session or request.session['username'] == None:
        request.session['redirect'] = request.get_full_path()
        return redirect('%s/ldap_login/'%ROOT);
    else:
        username = request.session['username'];
    
    s = request.POST; #get the form's submission data
    now = datetime.today()
    f = feedbackForm.objects.get(pk=form)
    answeredQuestions=list()
    
    for k,v in s.iteritems():
        pieces=k.split('_')
        if 'q' in pieces[0] and int(pieces[0].lstrip('q')) not in answeredQuestions:
               answeredQuestions.extend([int(pieces[0].lstrip('q'))])
    print "The answered questions ARE ........ ", answeredQuestions
    M=list(f.mandatoryQuestions())
    print "mandatory questions are ......", M
    print type(M)
    for mq in M:
        if mq not in answeredQuestions:
            return redirect("%s/manage_feedback/4/error"%ROOT); 
            break;
    
    submissionObj = feedbackSubmission.objects.get(pk=s['submissionID']); #create a new objecisting answer object
    submissionObj.when=now;
    submissionObj.save();

    #if mandatoriness is successfull,
    oldSubmissionAnswerOptions = feedbackSubmissionAnswer.objects.filter(submission=s['submissionID']);
    #discovery by Apoorva :)
    print "--> I am DELETING!";
    oldSubmissionAnswerOptions.delete(); #will directly delete all the corresponding submissions in teh QuerySet
      
    for k,v in s.items():
        #our form gives us a CSRF token and we don't want to process it here!
        if k == 'csrfmiddlewaretoken':
            continue;   
        if k == s['submissionID']:
            continue;
        pieces = k.split('_');
        
        #TODO : CODE TO CHECK MANDATORINESS!!
#which i right now not that important as students would be editing already filled forms. since the orms are not prefilled... the blank answer options would be treated as the previously filled one only.. and wont be considered as blank. and there is client side validation also.
        answeredQuestions=list()
       
        #delete old submission;
        if ('q' in pieces[0] and len(pieces) > 1):
            print "---> I am EDITSUBMIT!";
            print "pieces 0 is",pieces[0]
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
            print "---> Saving %s" % submissionAnswerObj;
            submissionAnswerObj.save(); #save this answer!

            print "Outside for loop!";
    t = loader.get_template('give_feedback/submit.html');
    c = RequestContext(request,
             {
                    'submissionID' : submissionObj.id,
                    'ROOT':ROOT
             }
           );
    return HttpResponse(t.render(c));

def submit(request,form):
    '''handles NEW feedback form submission'''
    
    #is the user NOT logged in ?
    if 'username' not in request.session or request.session['username'] == None:
        request.session['redirect'] = request.get_full_path()
        return redirect('%s/ldap_login/'%ROOT);
    else:
        #username = str(request.session['username']);
	#Kannan added the next 2 lines instead of the above line
    	username = request.session['username'];
        u=user.objects.get(pk=username)

    #get the form's submission data
    s = request.POST;     
    unfilled = u.get_unfilled_forms()
    print "in submisson view...unfilled forms are ",unfilled 
    
    f = feedbackForm.objects.get(pk=form)
    print "PROCESSING NEXT FORMS..!!"
    nextform = None
    if len(unfilled) is 0: #if unfilled forms list is empty!
        print "Exiting because len(unfilled) is 0..."    
    	nextform = None #then there is no next form!
    else:
        #this code is awesome..!!
        nextFormKaindex = -1;
        print " IN SUBMIT ....unfilled form ki list", unfilled

        if f in unfilled:
            print "f is... ", f, "NOT FILLED..!! "

            currentFormKaindex = unfilled.index(f)
            j = currentFormKaindex + 1 #start seeking from NEXT form
            print "current form ka index", currentFormKaindex, "j==", j
            for i in range(j,len(unfilled)):# to check the next editable/submitable form
                print "inside the loop.."
                #findout the next form to be filled which hasn't exceeded deadline!
                print "next unfilled form.",unfilled[i],"and uska deadline", unfilled[i].deadline_for_filling
                if unfilled[i].deadline_for_filling > datetime.today():
                   nextFormKaindex = i;
                   break;
            print "i am out of the loop and the next form ka index now is", nextFormKaindex
            #if this was the last form
            print 'unfilled length is %d and currentFormindex is %d and nextFormindex is %d' % (len(unfilled), currentFormKaindex, nextFormKaindex)
            if nextFormKaindex is -1:
               nextform=None
            else:   
               #there is AN editable form
               nextform = unfilled[nextFormKaindex];

            #request.session['unfilled'].remove(f)
               

        else:
			return redirect('%s/manage_feedback/1/error'%ROOT);       
    
    answeredQuestions=list()

    for k,v in s.iteritems():
        pieces=k.split('_')
        if 'q' in pieces[0] and int(pieces[0].lstrip('q')) not in answeredQuestions:
               answeredQuestions.extend([int(pieces[0].lstrip('q'))])
    print "The answered questions ARE ........ ", answeredQuestions
    M=list(f.mandatoryQuestions())
    print "mandatory questions are ......", M
    print type(M)
    for mq in M:
        if mq not in answeredQuestions:
            return redirect("%s/manage_feedback/4/error"%ROOT); 
            break;
    print "i ma getting printed.."

    #create a new submission object
    submissionObj = feedbackSubmission(); 
    submissionObj.feedbackForm = feedbackForm.objects.get(pk=s['formid']);
    submissionObj.submitter = user.objects.get(username__exact=username);
    submissionObj.save();
    print "request.POST === ", request.POST
    #put the submitted answers in the database
  
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

    # Remove this form from the list of unfilled forms...
    print "unfilled form ki list", unfilled
    print "current form ,f ", f
    
    #temporary fix for the bug #196
    if f in unfilled:
       unfilled.remove(f)

    request.session['unfilled']=unfilled
    print "unfilled form ki list after removing..!!", unfilled

    t = loader.get_template('give_feedback/submit.html');
    c = RequestContext(request,
         {
                'submissionID' : submissionObj.id,
                'nextform' : nextform,
                'ROOT':ROOT
         }
        );

    return HttpResponse(t.render(c));
