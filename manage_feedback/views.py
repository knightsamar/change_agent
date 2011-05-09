# Create your views here.
from manage_feedback.models import feedbackForm,feedbackQuestion,feedbackQuestionOption;
from give_feedback.models import feedbackSubmission,feedbackSubmissionAnswer
from ldap_login.models import user
from django.http import HttpResponse;
from datetime import datetime;
from django.template import Context, loader

#many of the things here are being managed by the admin panel...so we won't release it in version 0.1
#one view for Kulkarni Mam and coordinators to see how many and which students in a group hv filled 
#or not filled the form

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
       return HttpResponse("No submissions were made for this form!");
         
    #print whether deadline is gone or not for submitting...
    if f.deadline_for_filling < datetime.now():
        deadlineGone = True;
    else:
        deadlineGone = False;

    summary_outer_dict=dict()
    #for each feedbackQuestion in the form
    for q in f.questions.values():
        summary_inner_dict=dict();
        #find all AnswerOptions corresponding to it.
        qwaleOptions = feedbackQuestionOption.objects.filter(question = q['id'])
        #for each AnswerOption:
        for o in qwaleOptions:
                 #count the number of total feedbackSubmissionAnswer...
                 numberofSubmissionsChoosingThis = feedbackSubmissionAnswer.objects.filter(answer_option = o).count();
                 summary_inner_dict[str(o.text)]=numberofSubmissionsChoosingThis
        summary_outer_dict[str(q['text'])]=summary_inner_dict;         
    t = loader.get_template('manage_feedback/summary.html')
    c=Context(
                 {
                     'deadlinegone':deadlineGone,
                     'formName':f.title,
                     'summaryDict':summary_outer_dict
                 }
                 )

    return HttpResponse(t.render(c))        

#def notfilled(request, formID)
#''' to give out the list of ppl who have not filled the form... '''
        # get the form object rom the formid
        #generate an error if the form does not exists
        #get the deadline for filling the form

        #check for the form id in feedbackSubmissions
        #if no entry exu=ists.,.. generate the error......
        #else:
            # fetch all the users who all have filed the form
            # i.e. f=feeedbacksubmission.objects.filter(formid=formid)
            #and then f.submitter.

        # now get the list of the ppl who are supposed to fill the form
        # which is all the users who belong to the form.allowed_groups tuple.

        # display this list and provide a button to the admin saying "mail them" which would send mails to the users to fill the form before the deadline. :)

