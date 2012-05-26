#Justin here.  This is, as I understand it, the first django email handler. :-)

import sys, re, os

from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from email.Parser import Parser
from django.contrib.auth.models import User
from contact.models import MailHandler, MailMessage, AdditionalEmail
from social.models import TopLevelMessage
from people.models import RoleInGroup
from email_blast.models import BlastMessage
from django.db.utils import DatabaseError
from django.core.mail.backends import smtp

#Payload is potentially more complex than meets the eye.

def get_first_text_part(msg):
    '''
    Takes a message, returns the text portion
    
    TODO:Deal with the other parts of multipart messages
    '''
    maintype = msg.get_content_maintype() #Is this message multipart?
    if maintype == 'multipart': #If so, we're going to just grab the text.
        for part in msg.get_payload(): #TODO: Can this be dealt with as a dict?
            if part.get_content_maintype() == 'text':
                return part.get_payload()
    elif maintype == 'text':
        return msg.get_payload()


class Command(BaseCommand):
 
    def handle(self, *args, **options):
        p = Parser()
        
        #Parse the email from standard input
        
        if args:
            sample_email_filename = args[0]
            sample_email_file = open(sample_email_filename)
            email = p.parse(sample_email_file)
        else:
            email = p.parse(sys.stdin)       
        
        #f = open('/out.txt','w')
        
        #print >>f, email
        
        #Here are the relevant details.
        subject = email['subject']
        original_recipient_address = email['X-Original-To']

        body = get_first_text_part(email) + "\n\n This message was handled by Justin's Django Email handler (replace with some meaningful message)."
        sender = email['from']
        orig_sender = email['sender'] or email['from']
        
        #First of all, we're curious about whether this is a message sent to an object, in which case we're going to do something entirely different.
        subdomain=original_recipient_address.split('@')[1].split('.')[0]
        
        #There may be a drier way to confirm that the user has an account.
        #They do need one to send to blast or objects.
        if subdomain == 'blasts' or subdomain == 'objects':    
            try:
                sender_user = User.objects.get(email = orig_sender)
            except User.DoesNotExist:
                #This wasn't anybody's primary email.  Let's see if it's an additional email.
                try:
                    additional_email = AdditionalEmail.objects.get(email=orig_sender)
                    sender_user = additional_email.contact_info.userprofile.user
                except AdditionalEmail.DoesNotExist:
                    #If the use doesn't exist, we have no idea as whom to post the message.  We'll just have to tell them so.
                    recipients = []
                    subject = 'No dice.'
                    body = "It seems that your email address, %s, is not associated with a username.  Thus, you can't post a message." % (orig_sender)
                    sender = 'info@slashrootcafe.com'
                    recipients.append(orig_sender)
                    recipients.append('justin@justinholmes.com') #Send to Justin for debugging
                    for recipient in recipients:
                        send_mail(subject, body, sender, [recipient], fail_silently=False)#, connection=smtp.EmailBackend()) #To test smtp backend
                    return False
    
            if subdomain == 'blasts':
                blast_info = original_recipient_address.split('@')[0]
                group_name_with_underscores = blast_info.split('__')[0]
                group_name = group_name_with_underscores.replace('_', ' ')
                role_name = blast_info.split('__')[1]
                try:
                    role_in_group = RoleInGroup.objects.get(group__name=group_name, role__name=role_name)
                    blast_message = BlastMessage.objects.create(subject=subject, message=body, role=role_in_group.role, group=role_in_group.group, creator=sender_user)
                    blast_message.prepare()
                    blast_message.send_blast()
                    
                    return True
                    
                except RoleInGroup.DoesNotExist:
                    recipients = []
                    subject = 'No dice.'
                    body = "There is no role called %s and / or group called %s." % (role_name, group_name)
                    sender = 'info@slashrootcafe.com'
                    recipients.append(email['sender'])
                    recipients.append('justin@justinholmes.com') #Send to Justin for debugging
                    for recipient in recipients:
                        send_mail(subject, body, sender, [recipient], fail_silently=False)
                      
            
            if subdomain == "objects":
                object_info = original_recipient_address.split('@')[0]
    
                #Well, we seem to have found a sender_user, so we are going to go ahead with this shindig here.
                #Before we do, let's parse the message and get rid of any old replies or signatures.
                message_lines = body.split('\n')
                message_text = "" #Start an empty string which we'll fill with the message text.
                for line in message_lines:
                    if line[:2] == "--" or line[:1] == ">" or re.search(".*On.*(\\r\\n)?wrote:", line): #Let's see if the first two characters of the line are hyphens.
                        #If so, we're going to ignore anything after this line.
                        break #Since we have already found the end of the message, there's no need to keep iterating.
                    else:
                        #We haven't hit the hyphens yet, so we'll add this line to the message.
                        message_text += line + "\n"
    
                app_name = object_info.split('.')[0]
                model_name = object_info.split('.')[1]
                object_id = object_info.split('.')[2]
                Model=ContentType.objects.get(app_label=app_name, model=model_name.lower()).model_class()
                target_object = Model.objects.get(id=object_id)            
                TopLevelMessage.objects.create(content_object = target_object, creator=sender_user, message=message_text)
                return True
        else:
            #Nope, this is just a message to a user / group / handler (ie, not directly to an object).
            
            #Who is this email to?
            recipient_name=original_recipient_address.split('@')[0]
            
            recipients = []
             
            try:
                user = User.objects.get(userprofile__email_prefix__iexact=recipient_name)
                recipients.append(user.email)
            except User.DoesNotExist: #We don't need a MultipleObjectsReturned case because username is constrained unique.
                try:
                    handler = MailHandler.objects.get(address=recipient_name)
                    #TODO: Put amazing, mind-blowing shit here.
                    for user in handler.users.all():
                        recipients.append(user.email)
                except MailHandler.DoesNotExist:
                    subject = 'No dice.'
                    body = "We don't know " + email['to'] + ".  If you want to introduce us, send a message to info@slashrootcafe.com + \n Headers Follow: \n " + str(email)
                    sender = 'info@slashrootcafe.com'
                    recipients.append(email['sender'])
                    recipients.append('justin@justinholmes.com') #Send to Justin for debugging
                
                
            for recipient in recipients:    
                send_mail(subject, body, sender, [recipient], fail_silently=False)
                
            
            #Last of all - assuming the database is up, we'll save the message object now.
            if not subject:
                subject="No Subject."
            mail = MailMessage(subject=subject, body=body, recipient=original_recipient_address, sender=sender)
            
            try:
                mail.save()
            except: #TODO: Add reasonable and sane logging.  
                pass #Well, you know.  Fuck.