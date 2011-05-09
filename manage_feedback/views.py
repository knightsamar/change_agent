# Create your views here.
from manage_feedback.models import feedbackForm,feedbackQuestion,feedbackQuestionOption;
from give_feedback.models import feedbackSubmission,feedbackSubmissionAnswer
from django.http import HttpResponse;
from datetime import datetime;

#many of the things here are being managed by the admin panel...so we won't release it in version 0.1
#one view for Kulkarni Mam and coordinators to see how many and which students in a group hv filled 
#or not filled the form

def summary(request,formID):    
    """summary of feedback for a form..."""
    #select a form
    f = feedbackForm.objects.get(pk=formID);
    print 'we got %s in summary wala view' % (f);

    
    #do we have any submissions for this form ?
    submissions = feedbackSubmission.objects.filter(feedbackForm = f);

    #if number of submissions is more than 0,
    if len(submissions) < 0:
       return HttpResponse("No submissions were made for this form!");
         
    #print whether deadline is gone or not for submitting...
    if f.deadline_for_filling < datetime.now():
        deadlineGone = True;
    else:
        deadlineGone = False;

    summary = list();
    #for each feedbackQuestion in the form
    for q in f.questions.values():
        print "Q. ------",q['text']
        #find all AnswerOptions corresponding to it.
        qwaleOptions = feedbackQuestionOption.objects.filter(question = q['id'])
        #for each AnswerOption:
        for o in qwaleOptions:
                 print "...........",o.text,"..........",
                 #count the number of total feedbackSubmissionAnswer...
                 numberofSubmissionsChoosingThis = feedbackSubmissionAnswer.objects.filter(answer_option = o).count();
                 print numberofSubmissionsChoosingThis
                 #t = feedback
    return HttpResponse("heyy..!!")        

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

