from django.db import models

# Create your models here.
class feedbackSubmission(models.Model):
    feedbackForm = models.ForeignKey('manage_feedback.feedbackForm',help_text='Which Form\'s submission?');
    submitter = models.ForeignKey('ldap_login.user',help_text='Submitted by which user?');
    when = models.DateTimeField(auto_now_add=True, help_text='When was this submitted?');

class feedbackSubmissionAnswer(models.Model):
    submission = models.ForeignKey('feedbackSubmission',help_text='Submission for which this is the answer');
    question = models.ForeignKey('manage_feedback.feedbackQuestion',help_text='Question for which the answer was submitted');
    answer = models.ForeignKey('manage_feedback.feedbackQuestionOption',help_text='The answer submitted by the user');
    #use add method to insert rows/create instances...right?
