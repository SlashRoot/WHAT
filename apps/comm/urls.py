from django.conf.urls.defaults import *

urlpatterns = patterns('comm.views',
    (r'^phone/$', 'answer'), #Public call answering
    (r'^phone/test/$', 'answer', {'this_is_only_a_test': True}),
    #(r'^client_dial_out/$', 'client_dial_out'),
    #(r'^incoming_phone_client_loader/$', 'incoming_phone_client_loader'),
    (r'^simple_phone_lookup/$', 'simple_phone_lookup'),
    (r'^conference_blast/$', 'conference_blast'),
    (r'^voicemail/$', 'voicemail'),
    (r'^alert_pickup/(?P<number_id>\d+)/(?P<call_id>\d+)/$', 'alert_pickup'),
    (r'^handle_hangup/(?P<conference_id>\w+)/(?P<number_id>\d+)/$', 'handle_hangup'),
    
    (r'^pickup_connect/(?P<number_id>\d+)/(?P<call_id>\d+)/$', 'pickup_connect'),
    (r'^pickup_connect_auto/(?P<number_id>\d+)/(?P<call_id>\d+)/$', 'pickup_connect', {'connect_regardless': True}),
    
    (r'^transcription_handler/(?P<object_type>\w+)/(?P<id>\d+)/', 'transcription_handler'), 
    (r'recording_handler/(?P<object_type>\w+)/(?P<id>\w+)/$' ,'recording_handler'),
    
    (r'^simply_join_conference/(?P<conference_id>\w+)/(?P<number_id>\w+)/$', 'simply_join_conference'),
    
    #(r'status_callback/$', 'status_callback'),
    #(r'fallback/$', 'fallback'),

    (r'review_calls_with_user/(?P<user_id>\d+)/', 'review_calls_with_user'),

    (r'outgoing_call_menu/$', 'outgoing_call_menu'),
    
    #(r'browseDeviceCategory/', 'browseDeviceCategory'),
    #(r'modifyDevice/(?P<module_id>\d+)/', 'modifyDevice'),
    #(r'queryDevice/(?P<category_index>\d+)/', 'queryDevice'),

    #(r'outgoing_callback/$', 'outgoing_callback'),
    
    (r'phone_call_details/(?P<phone_call_id>\d+)/', 'phone_call_details'),
    
    (r'watch_calls/$', 'watch_calls'),
    (r'resolve_calls/$', 'resolve_calls'),
    (r'resolve_call/$', 'resolve_call'),
    
    #(r'outgoing_call/(?P<phone_number>\w+==)/', 'outgoing_call'),
    
    #Try with GET - feel like I've done this before?
    (r'outgoing_call/', 'outgoing_call'),
    #Urgent - go to all phones / record
    (r'second_leg_temp/$', 'redirect_to_tropo'),
    
)
