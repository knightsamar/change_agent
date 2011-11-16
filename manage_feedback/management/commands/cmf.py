#from manage_feedback.models import *
import csv
from manage_feedback.models import Batch , Subject
from datetime import date
from ldap_login.models import user
#FIXED_DEADLINE = Thursday 
def getBatchPrefix(prog,batch):
    pass

def a():
    #open the csv file
    csvFile = csv.DictReader(open('change_agent-data.csv','rb'));
    #for each line in d csv file
    for record in csvFile:
        subject = record['Subject'];
        teacher = record['Faculty'];
        div = record['Division'];
        #batch = getBatchPrefix(record['Programme'],record['Batch']);
        batch = record['Batch']
        d = date.today()
        y = d.year
        m = d.month
        if int(batch.split('-')[0]) == (y -1): # 2010
            #if m >=3 and m <=12:
            Sem = 3
            #else: Sem = 2
        elif int(batch.split('-')[0]) == (y -2): # 2009
            #if m >=3 and m <=12:
            Sem = 5
            #else: Sem = 4
        elif int(batch.split('-')[0]) == y: # 2011
            #if m >=3 and m <=12:
            Sem = 1
            #else: "oops ..;P"
        elif int(batch.split('-')[0]) == (y -3): # 2008
            #if m >=3 and m <=12: oops
            #else: Sem = 6
            pass;
        
        print subject, teacher, batch, Sem, div
        print "================="
        print 
        u = user.objects.get(pk = '10030142031')
        coursecode = '';
        try:
            print div
            from time import sleep
            
            if div:
                print "we got DIV as...", div
                
                b = Batch.objects.filter(programme = record['Programme']).filter(batchname = batch).filter(sem = Sem).get(division=div);
                print "already had",b
            else:
                print "Sorry NO Division"
                b = Batch.objects.filter(programme = record['Programme']).filter(batchname = batch).get(sem = Sem);
                print "already had",b
                
        except Exception as e:
            print e;
            
            print record['Programme']
            sleep(3);
            b = Batch(
                programme = record['Programme'],
                division = div,
                sem = Sem,
                course_coordinator = u,
                batchname = batch
                )
            b.save();
            try:
                coursecode = record['coursecode']
                print "We got coursecode as ", type(coursecode);
            except Exception as e:
                print "Exception is ",e
                coursecode = ""
        
        s = Subject(
            name = subject,
            for_batch = b,
            code = coursecode,
            taughtby = teacher,
            )
        s.save();
        
        print "Uploading" 
    

        '''
        #have we created a feedback form this subject for this batch already ?
        if record['Division'].strip() != '':
            fTitle = "%s (for %s %s Div %s)" % (subject, record['Programme'], record['Batch'], record['Division']);
        else:
            fTitle = "%s (for %s %s)" % (subject, record['Programme'], record['Batch']i);

        fAllowedGroups = group.objects.filter(name__iexact(batch));
        
        existing_forms = feedbackForm.objects.filter(title__startswith=subject).filter(allowed_groups         #if no
            #create a feedback form for the subject.
            f = feedbackForm();
            #assign the batch to it.
            #set deadline to FIXED_DEADLINE
        #if yes
            #store in duplicates
        #have we created a feedback form for this teacher for this batch already ?
        #if no,
        #create a feedback form for the subject.
            #assign the batch to it.
            #set deadline to FIXED_DEADLINE
        #if yes
            #store in duplicates
        '''    

