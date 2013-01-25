import sys
from path import path

PROJECT_ROOT = path(__file__).abspath().dirname().dirname()

VIRTUALENV = path(sys.executable).abspath().dirname().dirname()


sys.path.append(PROJECT_ROOT)
sys.path.append(PROJECT_ROOT / 'apps')

from heartbeat import Heartbeat
from what_apps.meta.alerts import local_red_alert
import requests



HEARTBEATS = Heartbeat.__subclasses__()

class HeartBeatRunner(object):
    error_messages = []

    def run(self):
        for HeartbeatChild in HEARTBEATS: 	#HeartbeatChild here is a class (a subclass of the Heartbeat class)
            
            heartbeat = HeartbeatChild()
            
            if not heartbeat.is_skipped():
#                try:
                heartbeat.run()
#                except Exception, e:
#                    self.error_messages.append(e)
                

                if not heartbeat.passed():
                    error_message = heartbeat.alert_failure()
                    self.error_messages.append(error_message)
                    
            
        #OK, now that we've run anything, let's figure out what kind of shape we're in.
        if self.error_messages:
            #Bad shape.  Time for red alert.
            alert_message = 'Heartbeat Failure. \n'
            for message in self.error_messages:
                alert_message += "%s \n" % message
            local_red_alert(alert_message)
        else:
            #Everything went ok - there are no error messages.
            report_response = requests.post(resources.HEARTBEAT_SUCSESS_URL)
                    
                    
                
if __name__ == "__main__":
    hbr = HeartBeatRunner()
    hbr.run()
