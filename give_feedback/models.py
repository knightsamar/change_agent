from django.db import models

# Create your models here.
class feedbackSubmission(models.Model):
    feedbackForm = models.ForeignKey('manage_feedback.feedbackForm',help_text='Which Form\'s submission?');
    submitter = models.ForeignKey('ldap_login.user',help_text='Submitted by which user?');
    when = models.DateTimeField(auto_now_add=True, help_text='When was this submitted?');
    def __str__(self):
        return ("%s's submission of form '%s'" % (self.feedbackForm, self.submitter))

class feedbackSubmissionAnswerOptions(models.Model):
    submission = models.ForeignKey('feedbackSubmission',help_text='Submission for which this is the answer');
    question = models.ForeignKey('manage_feedback.feedbackQuestion',help_text='Question for which the answer was submitted');
    answer = models.ForeignKey('manage_feedback.feedbackQuestionOption',help_text='The answer submitted by the user');
    answer_text = models.TextField('Answer text (only for text questions)',help_text='Text answer given by the user(only for text questions');

    def __str__(self):
        return ("%s's answer to '%s' in submission '%s'" % (self.submission.submitter, self.question.text, self.submission.id));

#limit_choices_to = {'answer.question_id__exact' : question});
    #use add method to insert rows/create instances...right?
