# Create your views here.
from manage_feedback.models import feedbackForm,feedbackQuestion,feedbackQuestionOption, feedbackAbout,Batch, Subject;
from give_feedback.models import feedbackSubmission,feedbackSubmissionAnswer
from ldap_login.models import user,group
from django.http import HttpResponse;
from django.shortcuts import redirect
from datetime import datetime;
from django.template import RequestContext,Context, loader
#from django.db.models import Q
from change_agent.settings import ROOT,MEDIA_URL, MEDIA_ROOT, COORDINATORS, createforms
from django.db.models import exceptions
from pyExcelerator import *
from django.views.decorators.cache import cache_page

#many of the things here are being managed by the admin panel...so we won't release it in version 0.1
#one view for Kulkarni Mam and coordinators to see how many and which students in a group hv filled 
def adminindex(request):
    if createforms is False:
        return HttpResponse("<b>Not allowed!</b>")
    
    if request.POST:
        post = request.POST
        print "==post=="
        for p,v in post.iteritems():
                print p,"==",v;
        
        
        createforms = post['createforms'];
        d = post['deadline'].split('-')
        deadline = datetime(int(d[0]),int(d[1]),int(d[2]));
        print deadline
        prog = post['programme']
        batchname = post['batch'] 
        
        
        try:
            teacherAbout = feedbackAbout.objects.get(title__startswith='Teacher');
        except:
            print 'creating teacherAbut'
            teacherAbout = feedbackAbout(title = 'Teacher', description = 'Feedback about teachers')
            teacherAbout.save()
        try:
            subjectAbout = feedbackAbout.objects.get(title__startswith='Subject');
        except:
            print 'creating StudentAbout'
            subjectAbout = feedbackAbout(title = 'Subject', description = 'Feedback about students');
            subjectAbout.save();
        #get all batches for this semester in this prog
        batches = Batch.objects.filter(programme = prog).filter(batchname = batchname)
        print "found batches === ", batches;
        if len(batches)==0:
            return HttpResponse('no batches')
        s = list()
        count =0
        subjectquestions = feedbackQuestion.objects.filter(name__startswith='subject')
        print "SUBJECT QUES == ", subjectquestions
        teacherquestions = feedbackQuestion.objects.filter(name__startswith='teacher')
        print "TEACHER QUESTIONS = ",teacherquestions
        for b in batches:
            subjects = Subject.objects.filter(for_batch=b);  #get the subjects for this batch 
            print "subject list for", b , subjects
            for s in subjects:
                #whole batch because in cases like current when we DO NOT have division or stream wise list of students
                c = {'MSc. (CA)':142, 'MBA-IT':141, 'BCA':122,'BBA-IT':121}
                yr = b.batchname[2:4]
                course = str(c[b.programme])
                groupname = yr+'030'+course
                whole_batch_group = group.objects.get(name=groupname);
     
                if createforms == 'all' or createforms == 'subject':
                    newForm = feedbackForm();
                    newForm.title = "%s (%s - %s %s)" % (s.name,b.programme,b.batchname,b.division)
                    
                    #get the proper groups for this batch
                    print 'division was', b.division
                    if len(b.division) == 1: #for one-letter divisions
                        groupname = "%s %s Div-%s" %(b.programme, b.batchname,b.division) # MBA 2010-12 Div-A
                    elif b.division == 'all': #for divisions with value 'all'
                        c = {'MSc. (CA)':142, 'MBA-IT':141, 'BCA':122,'BBA-IT':121}
                        yr = b.batchname[2:4]
                        course = str(c[b.programme])
                        groupname = yr+'030'+course
                    else: #in all other cases
                        groupname = "%s %s %s" %(prog,b.batchname,b.division)# MSc CA 2010-12 SA
                    print "groupname",groupname

                    try:
                        g = group.objects.get(name = groupname) #preference is given to the STREAM or division than the whole batch
                    except:        
                        print "got the group which isn't in ldap_login.groups...",groupname
                        print 'creating it...'
                        g = group(name = groupname)
                        g.save();

                    newForm.deadline = deadline
                    newForm.isofficial = True;
                    newForm.about = subjectAbout;
                    newForm.deadline_for_filling = deadline
                    newForm.save()
                    count = count+1
                    createdForSubject = True;
                    newForm.allowed_groups.add(g)
                    newForm.allowed_groups.add(whole_batch_group) #only for now, see above for reason
                    for q in subjectquestions:
                        newForm.questions.add(q); 

                if createforms == 'all' or createforms == 'teacher':
                    for t in s.taughtby.split(','): #for multiple teachers
                        newForm = feedbackForm();
                        newForm.title = "%s (%s - %s %s)" % (t,b.programme,b.batchname,b.division)
                    
                        #get the proper groups for this batch
                        if len(b.division) == 1:
                            groupname = "%s %s Div-%s" %(b.programme, b.batchname,b.division) # MBA 2010-12 Div-A
                        else:
                            groupname = "%s %s %s" %(prog,b.batchname,b.division)# MSc CA 2010-12 SA
                        try:
                            g = group.objects.get(name = groupname) #preference is given to the STREAM or division than the whole batch
                        except:
                            c = {'MSc. (CA)':142, 'MBA-IT':141, 'BCA':122,'BBA-IT':121}
                            yr = b.batchname[2:4]
                            course = str(c[b.programme])
                            groupname = yr+'030'+course
                            print "got the group",groupname
                            g = group.objects.get(name = groupname)

                        newForm.deadline = deadline
                        newForm.isofficial = True;
                        newForm.about = teacherAbout;
                        newForm.deadline_for_filling = deadline
                        newForm.save()
                        count = count +1
                        for t in teacherquestions:
                            newForm.questions.add(t)
                        newForm.allowed_groups.add(g)
                        newForm.allowed_groups.add(whole_batch_group) #only for now, see above for reason
        return HttpResponse('%s forms created' %count)   
    else:
        t=loader.get_template('manage_feedback/adminindex.html')
        c = RequestContext(request,{
                'ROOT':ROOT,
                'u':request.session['username']
                 });
        return HttpResponse(t.render(c));
def stusummary(request):
    if 'username' not in request.session:
       
        request.session['redirect'] = request.get_full_path()
        return redirect('%s/ldap_login/login'%ROOT) 
    # function to get the list of the subject for the entire batch.-all divisions and common.
    def getlist(g):
        p,b = g.getBatch()
        mybatch = Batch.objects.filter(programme = p, batchname = b)
        mysubs  = Subject.objects.filter(for_batch__in = mybatch)
        return mysubs
 
    
    
    # function to get the list of the questions that the student shoudl have answered for EACH subject/teacher
    def getQuest(forwhat):
        questionlist = feedbackQuestion.objects.filter(name__startswith = forwhat).exclude(type = 'text');
        toreturn = {} 
        for question in questionlist:
            returnstring = question.text + '\n'
            questionOptions = feedbackQuestionOption.objects.filter(question = question)
            for QO in questionOptions:
                returnstring += QO.text
            
            yield returnstring , question;    
            
            
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
    
    
    
    row = 3
    col = 2
    print "Subject List==", commonsub;

    #g = group.objects.filter(name__contains = batch,name__startswith = prgm);
    #for curr_group in g:
    #    print "Group", g
    for u in g.user_set.all():
    
        subjectQuestions = getQuest('subject')
        teacherQuestions = getQuest('teacher')

            
        row = row+2; 
        print "USER== ",u, row, col;
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
        print "we have total of ",scol,"subjects and ",tcol,"teachers";    
        row = row +1;
        bckr = row
        #print "startng to write the subs from row.", row 
        q_ans = wow(u,'subject')
        ques = []
        try:
            while 1:
                s,q = subjectQuestions.next()
                ques.append(q)
                col = 0
                w_sub.write(row,col,s)
                row = row+1
                #w_tea.write(row,col,str(u.username))
        except StopIteration:
           # print "Ended at",row
            lrow = row
            row = bckr
            pass;
        print "fiished with the questions" 
        for ncol in range(1,len(commonsub)):
            row = bckr
            print "writing from",row, col,
            try:
                value = q_ans.next()
            except StopIteration:
                break;
            for r in range(len(ques)):
                if value == '-':
                    w_sub.write(row,ncol,'-')
                else:
                    if ques[r] in value and value[ques[r]]:
                        a = value[ques[r]]
                    else:
                        a = '-'
                    w_sub.write(row,ncol,a)
                row = row+1
            col = col+1
            #print "to", row, col
        row = row+2
        col = 0
        '''
        q_ans = wow(u, 'teacher')
        try:
            while 1:    
                t,q = teacherQuestions.next()
                w_tea.write(row,col,t)
                row = row+1
                #w_tea.write(row,col,str(u.username))
        except StopIteration:
            pass;

        row = bckr   
        
        ncol =1
        try:
            while 1:
                row = bckr
                value = q_ans.next()
                for r in range(len(ques)):
                    if value == '-':
                        w_tea.write(row,ncol,'-')
                    else:
                        if ques[r] in value and value[ques[r]]:
                            a = value[ques[r]]
                        else:
                            a = '-'
                        w_tea.write(row,ncol,a)
                    row = row+1
                col = col+1
        except StopIteration:
            
             col = 0
             row = row +2
        '''     
    
    from change_agent.settings import MEDIA_ROOT,MEDIA_URL
    wb.save('%s/summary_sheets/%s - %s.xls'%(MEDIA_ROOT,prgm,batch))    
    return HttpResponse('<a href = "%s/summary_sheets/%s - %s.xls">Download Spreadsheet!</a><BR><br><br><br> <input type = "button" value = "back" onclick = "history.go(-1)">'%(MEDIA_URL,prgm,batch))

@cache_page(1)
def summary(request,formID):    
   
    """for rendering the index page for any user who has just logged in"""
     
    if 'username' not in request.session or request.session['username'] == None:
        request.session['redirect'] = request.get_full_path()
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
    from pygooglechart import PieChart2D;

    for q in f.questions.all():
        summary_inner_dict=dict();
        Options=feedbackQuestionOption.objects.filter(question=q)
        # to set the dictionalry initial value to 0. and the key to the question options
        for o in Options:
            summary_inner_dict[o]=0
        
        #find all AnswerOptions corresponding to it.
        
        sub=feedbackSubmission.objects.filter(feedbackForm=f)
        for s in sub:
            # the options to be counted is to be related to a partcular submission made for this partucal form.
            qwaleOptions = feedbackSubmissionAnswer.objects.filter(question = q).filter(submission=s);
            #for each AnswerOption:
            for opt in qwaleOptions:
                 #count the number of total feedbackSubmissionAnswer...
                 # adding the count to the inner dictionry
                 if opt.answer_text is not None:
                     summary_inner_dict[opt.answer_text]=None;
                     continue;
                 else:    
                     summary_inner_dict[opt.answer_option] = summary_inner_dict[opt.answer_option] + 1
        try:    
            chart = PieChart2D(450,200);
        
            def text(x): return x.text;
        
            print summary_inner_dict.values()
            print summary_inner_dict.keys()
        
            chart.add_data(summary_inner_dict.values())
            chart.set_pie_labels(list(map(text,summary_inner_dict.keys())))
            try:
                chart.download('%s/piecharts/%s.png'%(MEDIA_ROOT,q.id))
            except:
                pass;
        except: pass;       
    
        summary_outer_dict[q]=summary_inner_dict;
    t = loader.get_template('manage_feedback/summary.html')
    c=Context(
                 {
                     'deadlinegone':deadlineGone, # idk why we had put this condition...!! ??
                     'formName':f.title,
                     'summaryDict':summary_outer_dict,
                     'ROOT':ROOT,
                     'MEDIA_URL':MEDIA_URL
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


def notFilled(request):
        p = request.POST['programme']
        try:
           b = request.POST['batch']
        except KeyError:
            return HttpResponse('Please fill the batch also')
        queryset = feedbackForm.objects.filter(title__contains = '(%s - %s'%(p,b)).filter(isofficial = True);
        
        user_dict=dict()
        for existing_form in queryset:
            user_all=list()
            groups=existing_form.allowed_groups.values()
            for g in groups:
                # to extract users who were supposed to fill the form
                u=user.objects.filter(groups=g['id']).exclude(username__in= COORDINATORS.keys())
                user_all.extend(u)
            #now from this list.. remove ppl who have filled the form...!!
            forms=feedbackSubmission.objects.filter(feedbackForm=existing_form)
            for f in forms:
                try:
                 user_all.remove(f.submitter)
                except:
                    pass
            user_dict[str(existing_form.title)]=user_all
        t = loader.get_template('manage_feedback/notFilled.html');
        c = Context(
           {
             'forms_users_dict':user_dict
           }
         );
   
        return HttpResponse(t.render(c))
     
