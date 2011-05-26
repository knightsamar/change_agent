# Create your views here.
from manage_feedback.models import feedbackForm,feedbackQuestion,feedbackQuestionOption;
from give_feedback.models import feedbackSubmission,feedbackSubmissionAnswer
from ldap_login.models import user
from django.http import HttpResponse;
from django.shortcuts import redirect
from datetime import datetime;
from django.template import Context, loader

#many of the things here are being managed by the admin panel...so we won't release it in version 0.1
#one view for Kulkarni Mam and coordinators to see how many and which students in a group hv filled 

def summary(request,formID):    
    """summary of feedback for a form..."""
    #select a form
    f = feedbackForm.objects.get(pk=formID);
    print 'we got %s in summary wala view' % (f);

    # check if the user is actually allowed to view the form..!!
    u=user.objects.get(username=request.session['username'])
    feedbackAbout=u.allowed_viewing_feedback_about.values()
    allowed=False;
    for a in feedbackAbout:
        if str(a['title']) == str(f.title):
            allowed=True;
    if allowed is False:
        return HttpResponse("You are not allowed to see this submission ");
    #do we have any submissions for this form ?
    submissions = feedbackSubmission.objects.filter(feedbackForm = f).count();
    print "no of submissions are..!!!", submissions
    #if number of submissions is less than 0,
    if submissions <= 0:
       return redirect("/change_agent/manage_feedback/5/error");
         
    #print whether deadline is gone or not for submitting...
    if f.deadline_for_filling < datetime.now():
        deadlineGone = True;
    else:
        deadlineGone = False;

    summary_outer_dict=dict()
    #for each feedbackQuestion in the form
    for q in f.questions.values():
        summary_inner_dict=dict();
        Options=feedbackQuestionOption.objects.filter(question=q['id'])
        # to set the dictionalry initial value to 0. and the key to the question options
        for o in Options:
            summary_inner_dict[o]=0
        
        #find all AnswerOptions corresponding to it.
        
        sub=feedbackSubmission.objects.filter(feedbackForm=f)
        for s in sub:
            # the options to be counted is to be related to a partcular submission made for this partucal form.
            qwaleOptions = feedbackSubmissionAnswer.objects.filter(question = q['id']).filter(submission=s);
            #for each AnswerOption:
            for opt in qwaleOptions:
                 #count the number of total feedbackSubmissionAnswer...
                 # adding the count to the inner dictionry
                 if opt.answer_text is not None:
                     summary_inner_dict[opt.answer_text]=None;
                     pass;
                 else:    
                     summary_inner_dict[opt.answer_option] = summary_inner_dict[opt.answer_option] + 1
        summary_outer_dict[str(q['text'])]=summary_inner_dict;         
    t = loader.get_template('manage_feedback/summary.html')
    c=Context(
                 {
                     'deadlinegone':deadlineGone, # idk why we had put this condition...!! ??
                     'formName':f.title,
                     'summaryDict':summary_outer_dict
                 }
                 )

    return HttpResponse(t.render(c))        

def error(request, errorcode):
    print "errorcode is ", errorcode;
    print type(errorcode)
    errorcode=int(errorcode);
    print type(errorcode)
    msg=""
    if errorcode is 1:
        msg="This form is already filled"
    elif errorcode is 2:
        msg="Sorry Deadline Exceeded..!!"
    elif errorcode is 3:
        msg = "This url is not meant for u"
    elif errorcode is 4:
        msg = "Not all questions are answered"
    elif errorcode is 5:
        msg="No Submissions were made for this Form"
    t=loader.get_template('error.html')
    c=Context(
    {
        'msg':msg,    
    }
        );
    return HttpResponse(t.render(c));
