#from manage_feedback.models import *
import csv
from manage_feedback.models import Batch , Subject
from django.db.models import exceptions
from datetime import date
from ldap_login.models import user
from change_agent.settings import COORDINATOR
#FIXED_DEADLINE = Thursday 
def getBatchPrefix(prog,batch):
    pass
print "=========================="
coordinatior = {}
for k,v in COORDINATORS.iteritems():
    coordinators[v]=k;
def a():
    #open the csv file
    csvFile = csv.DictReader(open('manage_feedback/change_agent-data.csv','rb'));
    #for each line in d csv file
    for record in csvFile:
        subject = record['Subject'].strip();
        teacher = record['Faculty'].strip();
        div = ''
        div = record['Division'].strip();
        print "Division NOw is" , div;
        #batch = getBatchPrefix(record['Programme'],record['Batch']);
        batch = record['Batch'].strip()
        d = date.today()
        y = d.year
        m = d.month
        if int(batch.split('-')[0]) == (y -1): # 2010
            if m >=3 and m <=12:
                Sem = 3
            else: Sem = 2
        elif int(batch.split('-')[0]) == (y -2): # 2009
            if m >=3 and m <=12:
                Sem = 5
            else: Sem = 4
        elif int(batch.split('-')[0]) == y: # 2011
            if m >=3 and m <=12:
                Sem = 1
            #else: "oops ..;P"
        elif int(batch.split('-')[0]) == (y -3): # 2008
            if m >=3 and m <=12: print 'oops';
            else: Sem = 6
            pass;
        print subject, teacher, batch, Sem, div
        print "================="
        u = user.objects.get(pk = coordinator[batch])
        coursecode = '';
        try:
            print div
            from time import sleep
            
            if div:
                print "we got DIV as...", div
            else:   
                print 'Sorry No Division'
                div = 'all'

            b = Batch.objects.get(division=div, programme = record['Programme'], batchname = batch, sem = Sem);
            print "already have ",b 
        except exceptions.ObjectDoesNotExist:
            sleep(3)
            print "creating new"
            b = Batch(
                programme = record['Programme'],
                division = div,
                sem = Sem,
                course_coordinator = u,
                batchname = batch
                )
            #b.save();
            try:
                coursecode = record['coursecode']
                print "We got coursecode as ", type(coursecode);
            except Exception as e:
                print "Exception is ",e
                coursecode = ""
        except exceptions.MultipleObjectsReturned:
            print b
        s = Subject(
            name = subject,
            for_batch = b,
            code = coursecode,
            taughtby = teacher,
            )
        #s.save();
        
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

