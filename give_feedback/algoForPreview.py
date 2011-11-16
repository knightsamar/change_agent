from models import feedbackSubmission, feedbackSubmissionAnswer
def submissionMaker():
    #get the submission object.
    so = feedbackSubmission.objects.filter(pk=1);
    #get all the answers given by the user in the submission object.
    answers = feedbackSubmissionAnswer.objects.filter(submission=so)
    #create a blank dictionary:
    submissionDetails = [];
    #for each answer
    for a in answers:
        if a.answer_text == '' or a.answer_text is None: 
            d = {'question' : a.question.text, 'answer' : a.answer_option.text };
            #insert into the list
            submissionDetails.append(d);
            #question text
            #question answer value.
        else:
            d = {'question' : a.question.text, 'answer' : a.answer_text };
            submissionDetails.append(d);

    #print submissionDetails;
    return submissionDetails;

