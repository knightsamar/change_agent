#from manage_feedback.models import *
import csv
from manage_feedback.models import Batch , Subject
from django.db.models import exceptions
from datetime import date
from ldap_login.models import user
from change_agent.settings import COORDINATORS
from django.core.management.base import BaseCommand, CommandError
import traceback

class Command(BaseCommand):
    args = "CSVFile"
    help = '''
    Imports Subjects, Faculty Names and Batches from the given CSV File.
    For a proper sample file look at : http://redwine.sdrclabs.in/attachments/85/change_agent-data.csv

    You *need* to specify a CSVFile name along with path to process 
    '''
    
    def handle(self, *args, **options):
        if len(args) == 0:
            print self.help
            return
        semester = raw_input('Please enter the semester going on... (odd or even)');
        while semester != 'odd' and semester!= 'even':
            semester = '';
            semester = raw_input('(odd or even)');
        CSVFile = args[0];
        if CSVFile is None:
            print self.help
            return
 
        #FIXED_DEADLINE = Thursday 
        def getBatchPrefix(prog,batch):
            pass
        print "=========================="

        coordinators = {}
        for k,v in COORDINATORS.iteritems():
            coordinators[v]=k;
         
        try:
            #open the csv file
            csvFile = csv.DictReader(open(CSVFile,'rb'));
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
                if int(batch.split('-')[0]) == (y -1): # 2010
                   if semester == 'odd':  
                        Sem = 3
                   else: 
                        Sem = 2
                elif int(batch.split('-')[0]) == (y -2): # 2009
                   if semester == 'odd':  
                        Sem = 5
                   else: Sem = 4
                elif int(batch.split('-')[0]) == y: # 2011
                   if semester == 'odd':  
                        Sem = 1
                    #else: "oops ..;P"
                elif int(batch.split('-')[0]) == (y -3): # 2008
                   if semester == 'odd': pass;  
                   else: Sem = 6
                print subject, teacher, batch, Sem, div
                print "================="
                programme = record['Programme']
                u = user.objects.get(pk = coordinators[programme])
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
                    b.save();
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
                s.save();
                
                print "Uploading" 
        except Exception as e:
            print traceback.print_exc();

