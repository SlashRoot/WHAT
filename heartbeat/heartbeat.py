import sys, os, socket
import requests
import json
from path import path
from urllib2 import URLError
import uuid


from comm.sample_requests import TYPICAL_TWILIO_REQUEST
from xml.etree import ElementTree

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings.heartbeat'

from comm.services import find_command_in_tropo_command_list
from settings.common import ADMINS

from comm.comm_settings import SLASHROOT_EXPRESSIONS
from twill.commands import go, showforms, formclear, fv, show, submit, get_browser
from mechanize import Browser
from cookielib import LWPCookieJar
import json

import smtplib, imaplib

from django.http import HttpResponse
from settings.common import EMAIL_HOST

from private import resources, account_credentials

class Heartbeat(object):
    '''
    Parent object.  All actual heartbeats derive from this.
    '''
    error_details = ""
    
    def run(self):
        '''
        To 'run' a heartbeat is a two-step process:
        
        1) Obtain the criteria that we'll be testing.  We do this by applying tests to the live environment.
        2) Obtain the desired result of the testing.  Typically this is simply provided as a return statement on the desired_result() method, but it can be overridden for more specialized operation.
        '''
        self.actual_result = self.criteria()
        self.desired_result = self.desired_result()

        
    def passed(self):
        '''
        Compare the actual result with the desired result.
        '''
        if self.actual_result == self.desired_result:
            return True
        else:
            return False                    
       
    def is_skipped(self):
    	try:
    		if self.skip:
    			return True
    		else:
    			return False
    	except AttributeError:
    		return False
    
    def alert_failure(self):
        '''
        A wrapper around error_message.  This allows us to override the alert for certain tests if the heartbeat is too long or unwieldy.
        '''
        return self.error_message()
    
    def error_message(self):
        '''
        The default error is simply "result was x, desired result was y."  
        
        Good to override this to provide more intuitive alerts.
        '''
        return "%s failed: Result was %s, Desired result was %s" % (self.__class__.__name__, self.result, self.desired_result)
        
        
        
class WebsiteIsUp(Heartbeat):
    def criteria(self):
        urls = resources.URLS_TO_TEST
    	everything_is_cool = True #Assume we're OK until something goes wrong.
        self.responses = {}
        
        for name, url in urls.items():
            try: #The value for each key will either be....
                self.responses[name] = requests.get(url) #A response object, the result of requests.get()....
            except requests.exceptions.ConnectionError:
                everything_is_cool = False #We know things aren't cool here now. 
    
    	#If we have less than 3 total responses, we know that we encountered a connection error.  
    	if len(self.responses) < 3:
    		everything_is_cool = False
        else: #On the other hand, if we do have 3 responses, we need to make sure that they're all 200's.
            for response in self.responses.values():
        	    if not response.status_code == 200:
        		    everything_is_cool = False
    
    	return everything_is_cool
    
    def desired_result(self):
        return True
    
    def error_message(self):
        error_message = ""
        
        for key, value in self.responses.items():            
            if not value: #iow there is no response to a request for the website
                error_message += "%s is down.  " % key
            else:
                if value.status_code == 200:
                    error_message += "%s is up." % key
                else:
                    error_message += "%s raised a %s." % (key, value.status_code)
        return error_message
      
class UsersCanLogin(Heartbeat):
    """
    Tests except requests.exceptions.ConnectionError:that users can log in and view a restricted page
    """
    def criteria(self):
        '''
        return a tuple: 
        0) True if the server is up, otherwise False
        1) True if logging results in no errors, False otherwise
        2) Username if it can be discerned otherwise False
        '''
        criteria = {
        'server_is_up': False,
        'can_log_in': False,
        'username_as_discerned': False,
        }            
            
    	login_url = resources.LOGIN
    	
    	browser = Browser()
    	cookies = LWPCookieJar()
    	browser.set_cookiejar(cookies)      
        
        #First we'll see if the server is up at all.
        try:
            browser.open(login_url)
        except URLError:
            return criteria #Return all three as False         
        criteria['server_is_up'] = True #We got past the first block; we know that the server is up.
        
        
        #Second, we'll see if the login page properly accepts our login attempt.
        try:
            browser.select_form(name='login')
            browser['username'] = account_credentials.HEARTBEAT_USERNAME
            browser["password"] = account_credentials.HEARTBEAT_PASSWORD        
            response_to_login = browser.submit()
        except:
            return criteria #Server_is_up will be True, the other two are False.        
        criteria['can_log_in'] = True #We were able to login in the above block.


        #Last, we'll see if we are recognized as a logged-in user.            
        try:
            response_to_whoami = browser.open(resources.WHOAMI_API)
            user_info_dict = json.loads(response_to_whoami.read())
            username = user_info_dict["username"]
        except:
            return criteria #Only username_as_discerned is False.        
        criteria['username_as_discerned'] = username #We figured out the username

        
        #Everything went OK!
        return criteria
    
    def desired_result(self):
        result = {
        'server_is_up': True,
        'can_log_in': True,
        'username_as_discerned': account_credentials.HEARTBEAT_USERNAME,
        } 
        return result
    
    def error_message(self):
        if not self.actual_result['server_is_up']:
            error_message = "Users cannot login because the production server is down."
        else:
            error_message = "The production server is up, but users cannot log in."
            
        return error_message
        

class PhoneAnswering(Heartbeat):
    def criteria(self):
        """verifies that twilio and tropo are receiving the necessary signal"""
        request = TYPICAL_TWILIO_REQUEST
        try:
            response = requests.post(resources.PHONE_TEST_URL, request)
        except requests.exceptions.ConnectionError:
            return False
            
        response_xml = ElementTree.XML(response.content)
        say = response_xml[0]                
        expression = say.text
        return expression
    
    def desired_result(self):
        return SLASHROOT_EXPRESSIONS["public_greeting"]
    
    def error_message(self):
        if not self.actual_result:
            return "The comm app is not responding."

class EmailDelivery(Heartbeat):
    
    def criteria(self):        
        #Basic user details.
        receiver = account_credentials.RECEIVER_EMAIL
        email_user = account_credentials.SENDER_EMAIL #Forwarded from RECEIVER_EMAIL
        email_password = account_credentials.SENDER_EMAIL_PASSWORD
        
        #Generate a unique hash to identify this email.
        unique_email_id = uuid.uuid1().hex
        
        #First we need to read the hash file to see what hash we left from last time.
        try: #If this is the first time we've run, or if the hash has been deleted, we'll get IOError.
            heartbeat_hash_file = file(resources.HEARTBEAT_HASH_FILE, 'r')
        except IOError:
            heartbeat_hash_file = open(resources.HEARTBEAT_HASH_FILE, 'w')
            heartbeat_hash_file.write(unique_email_id)
            
            
        old_hash = heartbeat_hash_file.read()
        heartbeat_hash_file.close()

        #Now we'll log into email and see if a message exists with that old hash. 
        email = imaplib.IMAP4_SSL(resources.HEARTBEAT_IMAP_SERVER, resources.HEARTBEAT_IMAP_SERVER_PORT)
        login_response = email.login(email_user, email_password)
        
        if login_response[0] == "OK":
            email.select("Heartbeat")
            search_response = email.search(None, 'BODY', old_hash)
            if not search_response[1][0]: #This is supposed to return the number, in sequence, of the email.  If it's blank, the email didn't exist.
                self.error_details = "The previous email was not delivered."            
        else:
            self.error_details = "Unable to login to check %s." % resources.EMAIL_PROVIDER
          
        try:
            smtpserver = smtplib.SMTP(resources.HEARTBEAT_SMTP_SERVER, resources.HEARTBEAT_SMTP_SERVER_PORT)            
            smtpserver.ehlo()
            smtpserver.starttls()
            smtpserver.ehlo
            smtpserver.login(email_user, email_password)
                        
            msg = "Heartbeat Test ID: %s" % unique_email_id
            smtpserver.sendmail(email_user, receiver, msg) #We're not terribly concerned about who the mail comes from you.
            
            #If we got this far, we're assuming that we we're successful.
            success = True
            smtpserver.close()
            
            heartbeat_hash_file = open(resources.HEARTBEAT_HASH_FILE, 'w')
            heartbeat_hash_file.write(unique_email_id)
            heartbeat_hash_file.close()
        
    	except socket.error:
                self.error_details = "Error sending new email."

        everything_is_cool = not self.error_details #If there are error_details, we want to return False.
    	return everything_is_cool

    def desired_result(self):
        return True
    
    def error_message(self):
        return self.error_details
