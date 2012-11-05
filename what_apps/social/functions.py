from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from what_apps.do.models import Task
from what_apps.social.models import DrawAttention
T = ContentType.objects.get_for_model(Task)



def get_messages_for_user(user):
    '''
    Takes a user, returns a sorted list of tuples where the first element is an unread message and the second element is the datetime of the message's creation
    '''
    #Tasks
    #DrawAttentions to this user
    #Messages pointed at this user
    
    #We want all tasks..... #That this user has created,  #Posted a message on, #Or had their attention drawn to (we know by comparing it to the queryset above) #so long as they have at least one message
    tasks_with_messages = Task.objects.filter( \
                                               Q(ownership__owner = user) | \
                                               Q(messages__creator = user) | \
                                               Q(notices__target__user = user),\
                                               messages__isnull=False)\
                                               .distinct()\
                                               #TODO: Get the above queryset to exclude tasks which have only messages that have already been read by this user
                                        
    messages = []
    
    for task in tasks_with_messages:
        for message in task.messages.exclude(read_by_users__creator = user).exclude(creator=user).distinct(): #All messages that this user hasn't read
            messages.append( (message, message.created) )
        
    sorted_message_list = sorted(messages, key=lambda n: n[1], reverse=True)
    
    return sorted_message_list
        
                        
    
    
    
    
    

    