from django import http
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.conf import settings
from django.http import Http404

from what_apps.meta.alerts import local_red_alert

class ServerErrorMiddleware(object):
    def get_most_recent_line_in_traceback_from_what_codebase(self, traceback_string):
        traceback_lines = traceback_string.split('\n')
        for line in traceback_lines:
            if line is not None: #Tracebacks with no detail will be None.  We don't care about those.
                if len(line.split(settings.PROJECT_ROOT)) > 1: #See if we can split the string by the project root directory.
                    #...if so, this is the winner.
                    return line
    
    def get_useful_info_from_traceback_line(self, line):
        if line is not None: #Tracebacks with no detail will be None.  We don't care about those.
            remainder_of_the_line = line.split(settings.PROJECT_ROOT)[1] #The part of the line that comes after PROJECT ROOT
            file = remainder_of_the_line.split('"')[0]
            other_useful_info = remainder_of_the_line.split('"')[1][2:]
            return file, other_useful_info

    def process_exception(self, request, exception):
        if not settings.DEBUG and not exception.__class__ is Http404:
            traceback = self._get_traceback()
            line = self.get_most_recent_line_in_traceback_from_what_codebase(traceback)
            if line is None:
                message = "A critical error has occured in production.  No further information is available."
            else:
                file, other_useful_info = self.get_useful_info_from_traceback_line(line)
                
                #Now we have the useful info.  We need to tell the world.
                message = "A critical error has occurred in production. %s.  Likely culprit: %s on or near %s" % (str(exception), file, other_useful_info)
            local_red_alert(message) #Raise the alarm!
        return None #Use default exception handling.
    
    
        
    def _get_traceback(self):    
        """
        Helper function to return the traceback as a string
        From django snippet 638 by kcarnold
        """
        import traceback
        import sys
        return '\n'.join(traceback.format_exception(*(sys.exc_info())))

def page_not_found(request):
    t = loader.get_template('errors/404.html')
    return http.HttpResponseNotFound(t.render(RequestContext(request, {'request_path': request.path})))

def server_error(request):
    pass
    return HttpResponse('Llamas')