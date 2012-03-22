from django.template import loader, Context, RequestContext
import stomp
import json

def push_with_template(template, context, destination):
    '''
    Pushes content through stomp / morbidQ to comet listeners.
    This drives a lot of the "live" content on our site.
    '''
    t = loader.get_template(template) #Probably a very small, cookie-cutter template that gets included again and again.  'comm/call_alert.html' is a good example.
    c = Context(context)
    
    conn = stomp.Connection() #This will raise errors if stomp / orbited crash.  Maybe we should try / except and handle this situation more gracefully.
    conn.start()
    conn.connect()
    conn.send(t.render(c), destination=destination)
    conn.stop()
    
    return True

def push_with_json(dict, destination):    
    json_dict = json.dumps(dict)
    conn = stomp.Connection() #This will raise errors if stomp / orbited crash.  Maybe we should try / except and handle this situation more gracefully.
    conn.start()
    conn.connect()
    conn.send(json_dict, destination=destination)
    conn.stop()
    
    return True

def push_with_string(string, destination):
    conn = stomp.Connection() #This will raise errors if stomp / orbited crash.  Maybe we should try / except and handle this situation more gracefully.
    conn.start()
    conn.connect()
    conn.send(string, destination=destination)
    conn.stop()