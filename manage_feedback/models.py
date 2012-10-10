from django.db import models
from give_feedback.models import feedbackSubmission

#one feedbackquestion is applicable for many Forms and one Form can have many such questions
class feedbackQuestion(models.Model):
        name = models.CharField("Question Name", max_length=100, help_text='An identifier for the question for internal usage',unique=True);
        text = models.CharField("Question Text", max_length=200,help_text="The actual question");
        
        type = models.CharField(max_length=40, choices=
                ((u'multiple-choice-single-answer',u'Multiple-choice (single answer)'), #render a set of radio buttons
                (u'multiple-choice-multiple-answer',u'Multiple-choice (multiple answer)'),#render a set of checkboxes
                (u'text',u'Open-ended question')) #render a textarea which is wide
        );
        helptext = models.CharField(max_length=100, help_text="The text appears under the question", blank=True, null=True);
        mandatory = models.BooleanField(help_text="Whether you want to keep this field mandatory ?",default=False);

        def __str__(self):
            return ('ID %s %s - %s' % (self.id, self.name, self.type));

#one feedbackQuestionOption belongs to only one feedbackQuestion and that too for types which allow multiple-
class feedbackQuestionOption(models.Model):
        question = models.ForeignKey(feedbackQuestion,limit_choices_to = {'type__startswith':'multiple-'}); #make it applicable only for questions that support multiple choices
        text = models.CharField("Option Text", max_length=200, help_text="Specify the option here");

        def __str__(self):
            return self.text;
     

#one feedbackForm has many questions and it is viewable and fillable by many people
class feedbackForm(models.Model):
        title = models.CharField("Title as it appears to the filler",max_length=100,help_text='Title of the Form as it appears to the filler');
        #allowed_group = we will have a seperate table for relationship
        deadline_for_filling = models.DateTimeField(help_text='Deadline for filling and submitting the form');
        created_on = models.DateTimeField(auto_now_add=True);
        questions = models.ManyToManyField(feedbackQuestion);
        allowed_groups = models.ManyToManyField('ldap_login.group', help_text='Groups which are allowed to view and fill this form') #groups which are allowed to fill this form!
        about = models.ForeignKey('feedbackAbout');
        isofficial = models.BooleanField(default=True,blank=False,null=False, help_text="Is this an official form of SICSR or you are creating it just for your own non-official purpose?");
	sequence = models.CommaSeparatedIntegerField(max_length=100,blank=True,null=False,verbose_name='Sequence of questions',help_text='Sequence in which questions will appear.[ PLEASE ENTER COMMA SEPARATED VALUES ]',default='0')

        def __str__(self):
            return self.title; 

        def formsforUser(self,username): #are you sure it should be here ?
                #take username
                #check what groups are allowed to access this form object
                #
            pass;
        
        def has_been_filled_by_user(self, user):
            '''determines whether the given form was submitted by the give user or not
               if feedback was submitted, returns the feedbackSubmission object
               if feedback was not submitted, returns False

            '''
            try:
                submission = feedbackSubmission.objects.get(feedbackForm=self, submitter=user)
                return submission
            except feedbackSubmission.DoesNotExist as e:
                return False
            except feedbackSubmission.MultipleObjectsReturned as e:
                print 'This single user %s has MULTIPLE submissions!! -- Design problem detected!' % (user)
                print e.msg
                print e
                raise e

	def sortedQuestions(self):
		#if sequence is left empty it shows questions in default format
		if(self.sequence == ''):
                        return self.questions.all()
		else:	
			#get ids of all selected questions
                	selected_question_ids =[]
        	        for q in self.questions.all():
	                        selected_question_ids.append(q.id)

			#split the sequence
			sequence_split = self.sequence.split(',')
			sequence_ids = []
		
			#convert the split sequence into long and store it
			for s in sequence_split:
				sequence_ids.append(long(s))
		
			#endlist stores the ids of questions that are selected but not mentioned in sequence.We will put these ids at the end of sortedlist
			endlist =[]
		
			#ignorelist stores the ids of questions which are in sequence but not selected.We will ignore these questions for now
			ignorelist=[]
		
			#sortedlist stores the ids of questions in sorted order.
			sortedlist=[]

			#Stores ids which are selected but not in sequence
			for x in selected_question_ids:
				if(x in sequence_ids):
					pass
				else:
					endlist.append(x)
			#stores ids which are mentioned in sequence in order
			for y in sequence_ids:
				if(y in selected_question_ids):
					sortedlist.append(y)
				else:
					ignorelist.append(y)

			#stores ids not mentioned in sequence at the end of the sortedlist
			for z in endlist:
				sortedlist.append(z)
		
			sorted_questions = []
			for s in sortedlist:
				sorted_questions.append(feedbackQuestion.objects.get(pk=s))

			return sorted_questions;

	def save(self, *args, **kwargs):
           print "Saving a feedbackForm and putting the right sequence of questions"
          # for q in self.questions.values(): 
          #     self.sequence += q['id']
	   super(feedbackForm, self).save(*args, **kwargs)
	
	def mandatoryQuestions(self):
            """returns a list of mandatory feedbackQuestion in the form"""
            questions = self.questions.filter(mandatory=True);
            questions_dict = {};
            for q in questions:
                questions_dict[q.id] =  q.type;
            
            return questions_dict;

class feedbackAbout(models.Model):
        title = models.CharField("The thing/person about which Feedback is being collected",max_length=40);
        description = models.CharField(max_length=200,help_text="Description");
        #allowed_viewers =  users who are allowed to browse about thsi feedback -- will be back-referenced
        #which form? = which forms are used to collect feedback about this thing/person -- will be back-referenced
        
        def __str__(self):
            return self.title;

class Batch(models.Model):
    sem = ((1,1),(2,2),(3,3),(4,4),(5,5),(6,6))
    batchname = models.CharField(help_text='eg. 2010-12, 2006-09', max_length=7);
    programme = models.CharField('Programme', max_length =10)
    division = models.CharField(help_text='Division or Stream', max_length = 16);
    sem = models.IntegerField(choices = sem)
    course_coordinator = models.ForeignKey('ldap_login.user')
    #subjects = models.ForeignKey('Subject')
    def __str__(self):
        return "%s %s for Sem %d - %s" %(self.programme ,self.batchname ,self.sem, self.division)

    class Meta:
	verbose_name_plural = 'Batches'

class Subject(models.Model):
    name = models.CharField(max_length = 100);
    code = models.CharField(max_length = 15);
    for_batch = models.ForeignKey('Batch')
    taughtby = models.CharField(help_text="Use comma seperated for more than one teacher.",max_length=100)
    def __str__(self):
        return self.name + 'by' + self.taughtby
