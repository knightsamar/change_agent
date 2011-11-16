from django.template import RequestContext, Context, loader
from django.http import HttpResponse,HttpResponseNotFound
from django.shortcuts import redirect
from manage_feedback.models import feedbackForm,feedbackQuestion,feedbackQuestionOption, feedbackAbout, Batch, Subject
from give_feedback.models import feedbackSubmission, feedbackSubmissionAnswer
from django.core.context_processors import csrf

#from accepting submissions;
from give_feedback.models import *;
from ldap_login.models import user;
from settings import COORDINATORS
#for date
from datetime import datetime

def hamari404():
    #for customizing our 404
    return HttpResponseNotFound('<h2>Not found!</h2>');

def index(request):
    """for rendering the index page for any user who has just logged in"""
    
    if 'username' not in request.session or request.session['username'] == None:
        return redirect('/ldap_login/');
    else:
        print 'username in session object';
        username = request.session['username'];

    if username in COORDINATORS:
        print 'haha'
        t = loader.get_template('manage_feedback/adminindex.html');
        c = RequestContext(request,{});
        return HttpResponse(t.render(c));
    # to fetch the all the forms
    # for feedback About
    
    #TO ADD:- check for group as staff... not that important...:) 
    u=user.objects.get(pk=username)
    feedback_about_list=list()
    feedback_about=u.allowed_viewing_feedback_about.values();
    for a in feedback_about:
        try:
            ab=feedbackForm.objects.get(pk=a['id'])
            #feedback_forms_about=feedbackForm.objects.filter(about=ab)
            feedback_about_list.extend([ab])
        except:
            continue;
    try:
        about_us=feedbackForm.objects.get(title="About This Project") 
    except:
        print "create the about us form...;)"
        about_us = ""
        Filled = True;
    Filled=False
    # to fetch the filled forms for previewing and editing 
    
    filled_forms = list(feedbackSubmission.objects.filter(submitter=username));

    # to remove the filled forms from the list of all forms to get the newly available forms
    if filled_forms:
        request.session['filled']=list(filled_forms)
        print "filled form in index...", request.session['filled']
    print "dsadAS"
    #unfilled_forms = list(feedbackForm.objects.filter(allowed_groups=u.group));
    all_forms = list(feedbackForm.objects.all().exclude(title="About This Project"))
    print "all-forms.. ", all_forms
    print "user.", u
    print "user groups", u.groups.values()
    unfilled_forms=list();
    for g in u.groups.values():
        for f in all_forms:
            if g in f.allowed_groups.values():
                unfilled_forms.extend([f])
    print "unfilled forms..!!", unfilled_forms;
    for form in filled_forms:
    	k = form.feedbackForm
        if k == about_us:
            Filled = True
            filled_forms.remove(form)
	
        if k is not None and k in unfilled_forms:
		     unfilled_forms.remove(k)
     
    request.session['unfilled']= list(unfilled_forms);
    if Filled is False:
        print "=-----Filled is False----"
        request.session['unfilled'].append(about_us)            
    print request.session['unfilled']            
    # for displaying date and checking for deadline
    d = datetime.today();
    		
    t = loader.get_template('give_feedback/index.html');
    c = Context (
            {
                'username' : username,
	        	'About_us_filled' : Filled,
                'filled_list' : list(filled_forms),
        		'unfilled_list': list(unfilled_forms),
                'today' : d,
                'feedback_about_list':feedback_about_list
            }  ) #pass the list to the template
 
    return HttpResponse(t.render(c));

def adminindex(request):
    post = request.POST;
    print "==post=="
    for p,v in post.iteritems():
            print p,"==",v;
    
    createforms = post['createforms'];
    deadline = datetime.datetime(post['deadline']);
    semester = post['semester']
    prog = post['programme']
    batchname = post['batch'] 

    subject_qnos = [10043,10044,10045,10046,10047,10048,10049,10050]
    teacher_qnos = [10052,10053,10054,10055,10056,10057,10058,10064,10065,10066]
    subject_questions = []
    teacher_questions = []
    for q in subject_qnos:
        subject_questions.append(feedbackQuestion.objects.get(pk=q));

    for q in teacher_qnos:
        teacher_questions.append(feedbackQuestion.objects.get(pk=q));

    teacherAbout = feedbackAbout.objects.get(title__startswith='Teacher');
    subjectAbout = feedbackAbout.objects.get(title__startswith='Subject');

    #get all batches for this semester in this prog
    batches = Batches.objects.filter(programme = prog).filter(sem = semester).filter(batchname = batch)
    s = list()
    for b in batches:
        subjects = subject.objects.filter(for_batch=b);  #get the subjects for this batch 

        for s in subjects:
            if createforms == 'all' or createforms == 'subject':
                newForm = FeedbackForm();
                newForm.title = "%s (%s - %s %s)" % (s.name,b.programme,b.batchname,b.division)
                
                #get the proper groups for this batch
                g = group.get(pk = "%s - Div %s " % (b.programme, b.division))
                if g == []:
                    g = group.get(pk = bb.programme)

                newForm.allowed_groups = g
                newForm.deadline = deadline
                newForm.isofficial = True;
                newForm.about = teacherAbout;
                newForm.questions.add(subject_questions); 
                newForm.save()
                createdForSubject = True;

            if createforms == 'all' or createforms == 'teacher':
                for t in s.taughtby.split(','): #for multiple teachers
                    newForm = FeedbackForm();
                    newForm.title = "%s (%s - %s %s)" % (t, b.programme, b.batchname, b.division)
                    g = group.get(pk = b.division)
                    if g == []:
                        g = group.get(pk = b.division)
                    newForm.allowed_groups = g
                    newForm.deadline = deadline
                    newForm.isofficial = True;
                    newForm.about = subjectAbout;
                    newForm.questions.add(teacher_questions); 
                    newForm.save()
                    createdForTeacher = True;

def show(request,form):
    '''show feedback form FOR the FIRST TIME so that user can edit it'''     
    #are you allowed to VIEW this feedback form?

    #user is not logged in 
    if 'username' not in request.session or request.session['username'] == None: 
        return redirect('/ldap_login/'); 
    else: #is logged in!
        username = str(request.session['username']);
       
    #for feedback Forms Filling   
    f = feedbackForm.objects.get(pk=form);
    # is this form actually unfilled??

    print 'I am in show and f is %s' % (f);sdasddasd
    print 'and unfilled is %s' % (request.sessiasdasasdon['unfilled']);

    if f not in request.session['unfilled']:
        return redirect('/manage_feedback/1/error');
    mandatoryQuestions = f.mandatoryQuestions();

    # is the deadline exceded??
    now = datetime.today()
    
    if (f.deadline_for_filling < now ):
        return redirect("/manage_feedback/2/eror");
    else:
        flag='show'
        t = loader.get_template('give_feedback/form.html');
        c = RequestContext(request, #we use RequestContext to automagically prevent CSRF
           {
             'username': username,
             'form' : f,
             'flag' : flag,
             'mandatoryQuestions':mandatoryQuestions,
           }
         );
        return HttpResponse(t.render(c));

def preview(request,submissionID):
    if 'username' not in request.session or request.session['username'] == None:
        return redirect('/ldap_login/');
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
    	return redirect("/manage_feedback/3/error")#"boohoooooooooo..!! caught ya..!!! ")

    now = datetime.today();
    print "filled forms as per preview...", request.session['filled'];
    
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
        'submissionDetails':submissionDetails
        }
	);
    return HttpResponse(t.render(c));
    	
def edit(request):
    #handles editing of filled forms.. and updating the tables instead of creating new 
    # if the user is lot logged in.. redirect to login page

    if 'username' not in request.session or request.session['username'] == None:
        return redirect('/ldap_login/');
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
    	return redirect("/manage_feedback/3/error"); 
    
    now = datetime.today()
    ans = feedbackSubmissionAnswer.objects.filter(submission=submissionID);
    form = feedbackSubmission.objects.get(pk=submissionID).feedbackForm
   
    mandatoryQuestions = form.mandatoryQuestions();
    
    #have we exceeded the deadline already ???
    if (form.deadline_for_filling < now ):
        return redirect("/manage_feedback/2/error");
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
    	     'username':username
           }
         );

    return HttpResponse(t.render(c));
       
def editsubmit(request,form):
    """handles feedback form submission from EDITs"""

    #are we logged in ?
    if 'username' not in request.session or request.session['username'] == None:
        return redirect('/ldap_login/');
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
            return redirect("/manage_feedback/4/error"); 
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
             }
           );
    return HttpResponse(t.render(c));

def submit(request,form):
    '''handles NEW feedback form submission'''
    
    #is the user NOT logged in ?
    if 'username' not in request.session or request.session['username'] == None:
        return redirect('/ldap_login/');
    else:
        username = str(request.session['username']);
    
    #get the form's submission data
    s = request.POST;     

    print "in submisson view...unfilled forms are ", request.session['unfilled']
    
    unfilled = request.session['unfilled']
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
			return redirect('/manage_feedback/1/error');       
    
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
            return redirect("/manage_feedback/4/error"); 
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
    unfilled.remove(f)
    request.session['unfilled']=unfilled
    print "unfilled form ki list after removing..!!", unfilled

    t = loader.get_template('give_feedback/submit.html');
    c = RequestContext(request,
         {
                'submissionID' : submissionObj.id,
                'nextform' : nextform,
         }
        );

    return HttpResponse(t.render(c));
