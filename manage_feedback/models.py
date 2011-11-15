from django.db import models

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
            return ('%s - %s' % (self.name, self.type));

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

        def __str__(self):
            return self.title; 

        def formsforUser(self,username): #are you sure it should be here ?
                #take username
                #check what groups are allowed to access this form object
                #
            pass;
        
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
