# Create your views here.
from manage_feedback.models import feedbackForm,feedbackQuestion,feedbackQuestionOption, feedbackAbout,Batch, Subject;
from give_feedback.models import feedbackSubmission,feedbackSubmissionAnswer
from ldap_login.models import user,group
from django.http import HttpResponse;
from django.shortcuts import redirect
from datetime import datetime;
from django.template import Context, loader
#from django.db.models import Q

from pyExcelerator import *

#many of the things here are being managed by the admin panel...so we won't release it in version 0.1
#one view for Kulkarni Mam and coordinators to see how many and which students in a group hv filled 

def stusummary(request):
    
    
    # function to get the list of the subject for the entire batch.-all divisions and common.
    def getlist(g):
        p,b = g.getBatch()
        mybatch = Batch.objects.filter(programme = p, batchname = b)
        mysubs  = Subject.objects.filter(for_batch__in = mybatch)
        return mysubs
    try:
        batch = request.POST['batch']
        prgm = request.POST['programme']
    except KeyError:
        return HttpResponse('fill all fields :)')
    
    
    # function to get the list of the questions that the student shoudl have answered for EACH subject/teacher
    def getQuest(forwhat):
        questionlist = feedbackQuestion.objects.filter(name__startswith = forwhat);
        
        for question in questionlist:
            returnstring = question.text + '\n'
            questionOptions = feedbackQuestionOption.objects.filter(question = question)
            for QO in questionOptions:
                returnstring += QO.text
            
            yield returnstring, question;    
            
    # u pass the question and the Subject, this will return the option
    #def ithink(question,sub):
        

    wb = Workbook();
    w_sub = wb.add_sheet('Feedback for subjects by %s %s' %(prgm ,batch));
    w_tea = wb.add_sheet('Feedback for teachers by %s %s' %(prgm ,batch));

    c = {'MSc. (CA)':142, 'MBA-IT':141, 'BCA':122,'BBA-IT':121}
    yr = batch[2:4]
    course = str(c[prgm])
    groupname = yr+'030'+course
    print groupname
    g = group.objects.get(name = groupname)
    print "group", g
    commonsub   = getlist(g)


    
    
    f = str(prgm+batch) 
    w_sub.write(0,12,f)
    w_tea.write(0,12,f)

    row = 3
    col = 2
    print "Subject List==", commonsub;

    #g = group.objects.filter(name__contains = batch,name__startswith = prgm);
    #for curr_group in g:
    #    print "Group", g
    for u in g.user_set.all():
        
        subjectQuestions = getQuest('subject')
        teacherQuestions = getQuest('teacher')
    
    
        print "USER== ",u;
        print "="*50;
        col = 2
        w_sub.write(row,col-1,"Studnt's Name")
        w_sub.write(row,col,str(u.username))
        w_tea.write(row,col-1,"Student's Name")
        w_tea.write(row,col,str(u.username))

        row = row + 2
        scol = 1
        tcol = 1
        for subs in commonsub:
            w_sub.write(row,scol,subs.name)

            teachers  = subs.taughtby.split(',')
            if len(teachers)>1:
                for t in teachers:
                        w_tea.write(row,tcol,str(t))
                        tcol = tcol +1
            else:        
                w_tea.write(row,tcol,subs.taughtby)
                tcol = tcol+1
            scol = scol+1
        row = row +1;
        bckr = row
        col = 0

        try:
            while 1:    
                t,q = subjectQuestions.next()
                w_sub.write(row,col,t)
                row = row+1
                #w_tea.write(row,col,str(u.username))
        except StopIteration:
            row = bckr
            col = 0
            pass;
            
        try:
            while 1:    
                t,q = teacherQuestions.next()
                w_tea.write(row,col,t)
                row = row+1
                #w_tea.write(row,col,str(u.username))
        except StopIteration:
            pass;
            
    wb.save('lala.xls')    
    return HttpResponse('dfdsfsad')


def summary(request,formID):    
   
    """for rendering the index page for any user who has just logged in"""
     
    if 'username' not in request.session or request.session['username'] == None:
       return redirect('/change_agent/ldap_login');
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
        msg = "This url is not meant for you!"
    elif errorcode is 4:
        msg = "Not all questions are answered"
    elif errorcode is 5:
        msg="No Submissions were made for this form!"
    t=loader.get_template('error.html')
    c=Context(
    {
        'msg':msg,    
    }
        );
    return HttpResponse(t.render(c));
