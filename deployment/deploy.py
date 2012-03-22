import subprocess
import sys, os

print "using python binary: %s" % sys.executable #For logging on iguanadon.

from path import path

deployment_directory = path(__file__).abspath().dirname()

action = sys.argv[1]
deployment_type = sys.argv[2]

if deployment_type not in ['production', 'staging'] or action not in ['start', 'stop', 'restart']:
    exit('Usage: deploy.py (start / stop / restart) (production / staging)')

argument_details_tuple = deployment_directory, deployment_type

first_argument = '%s/%s.pid' % argument_details_tuple
second_argument = '%s/%s.tac' % argument_details_tuple

def start():
    subprocess.call(['twistd', '--pidfile', first_argument, '-y', second_argument, '--logfile', 'LOG_URL' % deployment_type])

def stop():
    try:
        pid_file = open('%s/%s.pid' % argument_details_tuple)
        pid = pid_file.read()
        subprocess.call(['kill', pid])
    except IOError:
        message = "\nYou can't restart %s because it is not currently running.  \nDid you mean 'start %s'?\n".replace('%s', deployment_type)
        exit(message) 

if action == "start":
    start()

if action == "stop":
    stop()
    
if action == "restart":
    stop()
    start()
