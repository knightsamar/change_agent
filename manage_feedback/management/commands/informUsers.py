from django.core.management.base import BaseCommand, CommandError
from ldap_login.models import group, user
from django.template import Context, Template
from django.template.loader import render_to_string
from django.core import mail
from change_agent.settings import DEFAULT_FROM_EMAIL
from smtplib import SMTPException

class Command(BaseCommand):
    args = "Group Code"
    help = '''
    Email the list of unfilled feedback forms to a group. You need to specify the group name or the string 'ALL'
    if you want to email all the users from all the groups.

    It will accept only the first group that is passed. Everything else on the commandline will be ignored.
    '''

    def handle(self, *args, **options):
        DEBUG = False
        if len(args) == 0:
            print self.help
            return False

        wanted_group = args[0]
        if wanted_group is None:
            print self.help
            return False

        if wanted_group == 'ALL':
           groups = group.objects.all();
        else:
           groups = group.objects.filter(name=wanted_group)

        if groups.count() is 0:
            print 'No such group called %s found!!!' % wanted_group
            print self.help
            return False
       
        #get email connection
        connection = mail.get_connection();
        for g in groups:
            print 'Group: ',g.name
            users = g.user_set.all()
            for u in users:
                unfilled_forms = u.get_unfilled_forms();
                if len(unfilled_forms) == 0:
                    continue;

                connection.open()
                
                print 'User: ', u.username
                if DEBUG : print 'Unfilled forms: ', unfilled_forms
                c = Context({
                    'user' : u,
                    'unfilled_forms' : unfilled_forms,
                })
                body = render_to_string("manage_feedback/informMail.html", c);
                to = '%s@sicsr.ac.in' % u.username 
                email = mail.EmailMessage(
                        subject = '[FeedbackForms] Please fill them!', 
                        body = body, 
                        from_email = DEFAULT_FROM_EMAIL, 
                        to = [to], 
                        connection = connection)
                
                try:
                    email.send()
                    print 'Done sending email!'
                except SMTPException as s:
                    print "Error while sending email : %s" % s
                    continue;
                #except Exception as e:
                #    print "Unhandled exception while sending email : %s" % e
                    continue;
        
        connection.close()
