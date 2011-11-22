# Create your views here.
from manage_feedback.models import feedbackForm,feedbackQuestion,feedbackQuestionOption, feedbackAbout,Batch, Subject;
from give_feedback.models import feedbackSubmission,feedbackSubmissionAnswer
from ldap_login.models import user,group
from django.http import HttpResponse;
from django.shortcuts import redirect
from datetime import datetime;
from django.template import Context, loader
#from django.db.models import Q
from django.db.models import exceptions
from pyExcelerator import *
from change_agent.settings import ROOT, MEDIA_ROOT, MEDIA_URL

#many of the things here are being managed by the admin panel...so we won't release it in version 0.1
#one view for Kulkarni Mam and coordinators to see how many and which students in a group hv filled 

def stusummary(request):
    
    
    # function to get the list of the subject for the entire batch.-all divisions and common.
    def getlist(g):
        p,b = g.getBatch()
        mybatch = Batch.objects.filter(programme = p, batchname = b)
        mysubs  = Subject.objects.filter(for_batch__in = mybatch)
        return mysubs
 
    
    
    # function to get the list of the questions that the student shoudl have answered for EACH subject/teacher
    def getQuest(forwhat):
        questionlist = feedbackQuestion.objects.filter(name__startswith = forwhat).exclude(type = 'text');
        toret = [] 
        toretQ = []
        for question in questionlist:
            returnstring = question.text + '\n'
            questionOptions = feedbackQuestionOption.objects.filter(question = question)
            for QO in questionOptions:
                returnstring += QO.text
            toret.append(returnstring)
            toretQ.append(question)
            
        return toret, toretQ;    
            
            
    # u pass the question and the Subject, this will return the option
    #def ithink(question,sub):
    
    
    try:
        batch = request.POST['batch']
        prgm = request.POST['programme']
    except KeyError as e:
        return HttpResponse('fill all fields :)....%s'%e)  

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
   


    def wow(u,forwhat):
        iterator = []
        if forwhat == 'subject':
            iterator=commonsub;
        else:
            for ss in commonsub:
                l = ss.taughtby.split(',')
                iterator.extend(l)
                
        #print "ITERATOR ====", iterator       
        
        for s in iterator:
            Title = "%s (%s - %s" % (s,prgm,batch) 
            d = datetime.today()
            d = datetime(d.year,d.month-3,d.day)
            try:
                if forwhat == 'subject':
                    f = feedbackForm.objects.filter(title__startswith = s.name , created_on__gt = d)
                    #print 'feedbackform',f
                else:
                    print Title
                
                    f = feedbackForm.objects.filter(title__contains = str(Title.strip()),created_on__gt = d)
            except exceptions.MultipleObjectsReturned as e:
                    print e
            except exceptions.ObjectDoesNotExist:
                pass;
            try:
                fs = feedbackSubmission.objects.get(feedbackForm__in =  f, submitter = u, when__gt = d)
                #print "feeback submission",fs
                fsa = feedbackSubmissionAnswer.objects.filter(submission = fs)
                #print "Answer",fsa
                toreturn = {}
               
                for answers in fsa:
                    if answers.question.type == 'multiple-choice-single-answer':
                        toreturn[answers.question] = answers.answer_option.text
                    elif answers.question.type == 'multiple-choice-multiple-answer':
                        try:
                            toreturn[answers.question]+=answers.answer_option.text
                        except KeyError:
                            toreturn[answers.question] = answers.answer_option.text

            except exceptions.ObjectDoesNotExist:
                #print e;
                toreturn = '-'
            yield toreturn;

    
    
    f = str(prgm+batch) 
    w_sub.write(0,6,f)
    w_tea.write(0,6,f)
    
    
    #rows and columns for subject 
    Srow = 3
    Scol = 2
    #rows and columns for teachers
    Trow = 3
    Tcol = 2

    print "Subject List==", commonsub;

    subjectQuestions, quesS = getQuest('subject')
    teacherQuestions, quesT = getQuest('teacher')


    #g = group.objects.filter(name__contains = batch,name__startswith = prgm);
    #for curr_group in g:
    #    print "Group", g
    for u in g.user_set.all():

        
            
        Trow = Trow+2; 
        Srow = Srow+2;
        print "USER== ",u, Srow, Scol;
        print "="*50;
        Scol = 2
        Tcol = 2

        w_sub.write(Srow,Scol-1,"Studnt's Name")
        w_sub.write(Srow,Scol,str(u.username))
        w_sub.write(Srow,Scol+1,str(u.fullname))
        w_tea.write(Trow,Tcol-1,"Student's Name")
        w_tea.write(Trow,Tcol,str(u.username))
        w_sub.write(Trow,Tcol+1,str(u.fullname))

        Srow = Srow + 2
        Trow = Trow + 2
        Scol = 1
        Tcol = 1


        ################# SUBJECT ###########################
        
        
        for subs in commonsub:
            w_sub.write(Srow,Scol,subs.name)

            teachers  = subs.taughtby.split(',')
            if len(teachers)>1:
                for t in teachers:
                        w_tea.write(Trow,Tcol,str(t))
                        Tcol = Tcol +1
            else:        
                w_tea.write(Trow,Tcol,subs.taughtby)
                Tcol = Tcol+1
            Scol = Scol+1
        #print "we have total of ",Scol,"subjects and ",Tcol,"teachers";    
        Srow = Srow +1;
        Trow = Trow +1
        bckr = Srow 
        backup = Trow
        #print "startng to write the subs from row.", row 
        q_ans = wow(u,'subject')
        # first print the question strint at col0
        Scol = 0
        
        for i in range(0,len(subjectQuestions)):
           try: 
                print subjectQuestions[i]
                
                w_sub.write(Srow,Scol, subjectQuestions[i])
                Srow = Srow+1
                #w_tea.write(row,col,str(u.username))
           except IndexError:
                continue
        print "fiished with the questions" 
        for ncol in range(1,len(commonsub)):
            print "ncol==",ncol,"row", Srow
            Srow = bckr
            #print "writing Subject from",Srow, Scol,
            try:
                value = q_ans.next()
            except StopIteration:
                break;
            for r in range(len(quesS)):
                if value == '-':
                    w_sub.write(Srow,ncol,'-')
                else:
                    try:#print "VVVV",value
                        w_sub.write(Srow,ncol,value[quesS[r]])
                    except KeyError:
                        w_sub.write(Srow,ncol,'-')
                Srow = Srow+1
            Scol = Scol+1
            #print "to", row, col
        Srow = Srow+2
        Scol = 0
        # end of subject Saving....... now only on next ireration..
        
        #####################  TEACHER  #########################
        
        q_ans = wow(u, 'teacher')
        Trow = Trow +1
        
        Tcol = 0
        try:
            Trow = backup
            i = 0
            for i in range(0,len(teacherQuestions)):
                #teacherQuestions[i]
                w_tea.write(Trow,Tcol,teacherQuestions[i])
                Trow = Trow+1
                i = i+1
                #w_tea.write(row,col,str(u.username))
        except Exception as e:
            print "had found an exception..",e
        #Trow = Trow+1 
        Trow = Trow + 2 
        
        Tcol = 1
        
        while 1:
                Trow = backup
                try:
                    value = q_ans.next()
                except StopIteration:
                    break;
                for r in range(len(quesT)):
                    if value == '-':
                        w_tea.write(Trow,Tcol,'-')
                    else:
                        try:
                            w_tea.write(Trow,Tcol,value[quesT[r]])
                        except KeyError:   
                            print "found no answer to THIS qestions......",quesT[r]
                    Trow = Trow+1
                Tcol = Tcol + 1
        
        Trow = Trow +10
    
    wb.save('%s/%s - %s.xls'%(MEDIA_ROOT,prgm,batch))    
    return HttpResponse('<a href = "%s/%s - %s.xls">click</a><BR><input type = "button" value = "back" onclick = "history.go(-1)">'%(MEDIA_URL,prgm,batch))


def summary(request,formID):    
   
    """for rendering the index page for any user who has just logged in"""
     
    if 'username' not in request.session or request.session['username'] == None:
       return redirect('%s/ldap_login'%ROOT);
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
       return redirect("%s/manage_feedback/5/error"%ROOT);
         
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
                     'summaryDict':summary_outer_dict,
                     'ROOT':ROOT
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
