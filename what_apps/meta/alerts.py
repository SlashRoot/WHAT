"""
Actions to take during different alert statuses.

These actions may be taken when the database is down, so some values are hardcoded.
"""
from what_apps.comm.services import place_call_to_number
from settings.admin_contacts import PRODUCTION_EMERGENCY
from django.core.mail.message import EmailMessage
import requests
from twisted.internet.threads import deferToThread
from twisted.internet import reactor

def place_red_alert_phone_call(phone_recipients, message):
    '''
    Takes a list of phone_recipients in the form "5551234567" and a string (message) and places the call.
    returns None
    '''
    for recipient in phone_recipients:
        requests.post('https://api.tropo.com/1.0/sessions/', 
                      data={
                            'token':'0a6a9ef88a0cd141b25e11ec47b28295a7ece5d29820bc1d5d5fec0f6dc6ae2156d120a270d0ec2bb5241e5c', 
                            'numberToCall':recipient, 
                            'messageToReadToCaller':message
                            }
                      )

def local_red_alert(message):
    '''
    Sends out an SMS message, email, and initiates a conference call.
    '''
    message = message.replace('/', ' slash ').replace('.py', ' dot pie.') #To assist the text-to-speech
    sms_recipients = []
    phone_recipients = []
    email_recipients = []
    
    for contact in PRODUCTION_EMERGENCY:
        if contact[1]:
            phone_recipients.append(contact[1])
        if contact[2]:            
            email_recipients.append(contact[2])
        if contact[3]:
            sms_recipients.append(contact[3])
    
    place_red_alert_phone_call(phone_recipients, message)
    subject = "" 
    body = message
    sender = 'red_alert@slashrootcafe.com'
    
    sms_msg = EmailMessage(subject, body, sender, sms_recipients)
    sms_msg.send()
    
    email_msg = EmailMessage(subject, body, sender, email_recipients)
    email_msg.send()

    return True