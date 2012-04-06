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
        
        CSVFile = args[0];
        if CSVFile is None:
            print 'You need to specify path to a CSV File!!!'
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
                print "Processing Record : ", record
                subject = record['Subject'].strip();
                teacher = record['Faculty'].strip();
                div = ''
                div = record['Division'].strip();
                print "Division Now is" , div;
                #batch = getBatchPrefix(record['Programme'],record['Batch']);
                batch = record['Batch'].strip()
                d = date.today()
                y = d.year
                m = d.month
                #determine the semester of the batch
                if int(batch.split('-')[0]) == (y-1): # 2010
                    if m >= 6 and m <=12:
                        Sem = 3
                    else: 
                        Sem = 2
                elif int(batch.split('-')[0]) == (y-2): # 2009
                    if m >= 6 and m <=12:
                        Sem = 5
                    else: 
                        Sem = 4
                elif int(batch.split('-')[0]) == y: # 2011
                    if m >= 6 and m <=12:
                        Sem = 1
                    #else: "oops ..;P"
                elif int(batch.split('-')[0]) == (y-3): # 2008
                    if m >= 6 and m <=12: 
                        print 'oops';
                    else: 
                        Sem = 6
                    pass;
                print subject, teacher, batch, "Sem ", Sem, div
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
                    print "Using existing Batch ",b 
                except exceptions.ObjectDoesNotExist:
                    sleep(3)
                    print "Creating new Batch"
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
                        print "We have coursecode as ", type(coursecode);
                    except Exception as e:
                        print "Exception is ",e
                        coursecode = ""
                except exceptions.MultipleObjectsReturned:
                    print b
                
                #Create subject record
                print "Creating new Subject"
                s = Subject(
                    name = subject,
                    for_batch = b,
                    code = coursecode,
                    taughtby = teacher,
                    )
                s.save();
                
                print "Saved."
                print "*" * 42
        except Exception as e:
            print traceback.print_exc();
