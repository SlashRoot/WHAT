from django.conf.urls.defaults import *
from django.conf import settings

from django.views.generic.simple import direct_to_template

from django.contrib import admin
from django.views.generic.edit import CreateView


admin.autodiscover()

from sandbox.models import TempContactInfo




urlpatterns = patterns('',
    (r'^mesh_summit_contact/$', CreateView.as_view(model=TempContactInfo)),

    #MAIN
    (r'^$', 'main.views.main_landing'),
    
    #CMS
#    (r'^hack-and-tell/apply/$', 'cms.views.q_and_a_form', {'q_and_a_id': 1}),
    (r'^/cms/form/(?P<q_and_a_id>\d+)/$', 'cms.views.q_and_a_form'), #Public
    (r'^hack-and-tell/$', 'main.views.hack_and_tell'), #Public
    
    (r'^cms/edit_content_block/(?P<headline_slug>\w+)/$', 'cms.views.edit_content_block'),
    (r'^cms/edit_content_block/$', 'cms.views.edit_content_block'),
    
    (r'^blog/(?P<headline_slug>[-\w]+)/$', 'cms.views.blog'), #Public
    (r'^blog/$', 'cms.views.blog'), #Public
    
    #(r'^admin/varnish/', include('varnishapp.urls')),
    
    
    
    #Accounting
    (r'^accounting/show_donations', 'accounting.views.show_donations'),
       
    #Generic Ajax Handler - include object type in URL (This is used to update objects via ajax in a generic way)
    (r'^utility/submit_generic/(?P<app_name>\w+)/(?P<object_type>\w+)/$', 'utility.views.submit_generic'),
    (r'^utility/submit_generic_partial/(?P<object_type>\w+)/(?P<object_id>\d+)/$', 'utility.views.submit_generic_partial'),
    
    #Commerce
    (r'^commerce/record_purchase/$', 'commerce.views.record_purchase'),
    (r'^commerce/record_bill/$', 'commerce.views.record_purchase', {'is_bill': True}),
    (r'^commerce/record_donation', 'commerce.views.record_donation'),
    (r'^commerce/record_ingredient_order', 'commerce.views.record_ingredient_order'),
    (r'^commerce/view_exchange/(?P<id>\d+)/$', 'commerce.views.view_exchange'),
    (r'^commerce/view_purchase/(?P<seller_involvement_id>\d+)/$', 'commerce.views.view_purchase'),
    (r'^commerce/view_pledge/(?P<pledge_id>\d+)/$', 'commerce.views.view_pledge'),
    (r'^commerce/individual_delivery', 'commerce.views.individual_delivery'),
    (r'^commerce/fluidbarter', 'commerce.views.fluidbarter_main'), 
    
    #Commerce: Front-facing eshu
    (r'^eshu$', 'commerce.views.eshu_main'),
    (r'^eshu/list_purchases/(?P<party_id>\d+)/$', 'commerce.views.list_purchases'),

    #Static
#    (r'^media/css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s/static/css' % settings.PROJECT_ROOT}),                           
#    (r'^media/js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s/static/js' % settings.PROJECT_ROOT}),
#    (r'^media/images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s/static/images' % settings.PROJECT_ROOT}),                
#    (r'^media/fonts/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s/static/fonts' % settings.PROJECT_ROOT}),
#    (r'^media/code/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s/static/code' % settings.PROJECT_ROOT}),
#    (r'^media/public/images/profile/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s/static/public/images/profile' % settings.PROJECT_ROOT}),
#    (r'^media/public/images/message_files/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s/static/public/images/message_files' % settings.PROJECT_ROOT}),
#    (r'^meta/docs/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s/docs/_build/html' % settings.PROJECT_ROOT}),

    #Temp way to serve admin media files (we'll do it through nginx later, along with all other media files -Justin) (TODO: Or Twisted?)
    #(r'^media_admin/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/usr/local/lib/python2.6/dist-packages/django/contrib/admin/media'}),
    
    #Admin
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    
    #Contact
    (r'^contact/contact_list', 'contact.views.contact_list'),
    (r'^contact/contact_profile/(?P<contact_id>\d+)/', 'contact.views.contact_profile'),
    (r'^contact/contact_profile/(?P<username>\w+)/', 'contact.views.contact_profile'),
    (r'^contact/new_contact/', 'contact.views.new_contact'),
    (r'contact/toggle_dial_list/(?P<dial_list_id>\d+)/', 'contact.views.toggle_dial_list'),
    (r'contact/contact_forms_for_person/', 'contact.views.contact_forms_for_person'),
    (r'contact/phone_number_profile/(?P<phone_number_id>\d+)/', 'contact.views.phone_number_profile'),
    
    #Menu on TV
    (r'^bar_menu', 'pos.views.bar_menu'),
      
    
    #Login-related views
        #Presence
    (r'^bare_login', 'presence.views.bareLogin'), #Public
    (r'^bareLogout', 'presence.views.bareLogout'),
    
    (r'^api/whoami/', 'people.views.who_am_i'),
    (r'^api/remote_heartbeat_success', 'meta.views.remote_heartbeat_success'),
    
    
    #Main
    (r'^loggedInBubbles', 'main.views.loggedInBubbles'),
    (r'^rightSideWidgets', 'main.views.rightSideWidgets'),
        
    
    #People
    #(r'^members/', 'people.views.members'),
    #(r'^users/(?P<username>\w+)/$', 'people.views.memberProfile'),
    #(r'^apply/', 'people.views.memberApply'),
    #(r'^curriculum/', 'people.views.memberCurriculm'), 
    (r'^people/role_form/$', 'people.views.role_form'),
    (r'^people/awesome/$', 'people.views.awesome_o'),
    
    #POS
    (r'^pos/pos_modal', 'commerce.views.pos_modal'),
    #Temporary solution until better way
    (r'^pos/$', 'pos.views.pos_landing'),
    (r'^pos/sales/$', 'pos.views.sales'),
    
    #Presence
    (r'^presence/askPurpose', 'presence.views.askPurpose'),
    (r'^presence/tellPurpose', 'presence.views.tellPurpose'),
    (r'^presence/viewSessions', 'presence.views.viewSessions'),
    (r'^presence/login', 'django.contrib.auth.views.login', {'template_name': 'presence/login_page.html'}),
    (r'^presence/close_slashroot', 'presence.views.close_slashroot'),
    
    #hwtrack
    (r'^hwtrack/all_devices', 'hwtrack.views.all_devices'),
    (r'^hwtrack/all_computers', 'hwtrack.views.all_computers'),
    #(r'^service/service_check_in', 'hwtrack.views.service_check_in'),
    
    #Service
    #(r'^serviceCheckIn', 'hwtrack.views.ServiceCheckIn'),
    (r'^computerOwner', 'hwtrack.views.Computer_Owner'),
    #This is for a client to track their computer through the site. It will be 
    #something along these lines I suppose- AC, KP 
    #(r'^hardwareTracking', 'hwtrack.views.hardware_Tracking')
    (r'^service/check_in/$', 'service.views.most_basic_check_in'),
    (r'^service/the_situation/$', 'service.views.the_situation'),
    (r'^service/archive/$', 'service.views.archive'),
    (r'^service/tickets/(?P<service_id>\d+)/$', 'service.views.tickets'),
    (r'^service/post_task_message/(?P<service_id>\d+)/', 'service.views.post_task_message'),
    
    
    #Social
    (r'^social/draw_attention_ajax/', 'social.views.draw_attention_ajax'),
    (r'^iam/$', 'social.views.dashboard'),
    (r'^social/messages/post_top_level/(?P<object_info>\w+)/', 'social.views.post_top_level_message'),
    (r'^social/acknowledge/(?P<attention_id>\d+)/', 'social.views.acknowledge_notification'),
    (r'^social/log/user/(?P<username>\w+)/$', 'social.views.log'),
    (r'^social/log/group/(?P<group_name>\w+)/$', 'social.views.log'),
    #(r'^social/log/$', 'social.views.log'),
    #(r'^social/log/log_landing/', 'social.views.log')
    
    
    #Phone
    (r'^comm/', include('comm.urls')), 
    
    
    #do
    (r'^do/$', 'do.views.landing'),
    (r'^do/big_feed/$', 'do.views.big_feed'),
    (r'^do/public_list/$', 'do.views.public_list'),
    (r'^do/get_people_for_verb_as_html/(?P<verb_id>\d+)/$', 'do.views.get_people_for_verb_as_html'),
    
    (r'^do/task_form_handler', 'do.views.task_form_handler'),
    (r'^do/create_task', 'do.views.create_task'),
    (r'^do/task_prototype_list', 'do.views.task_prototype_list'),

    (r'^do/task_profile/(?P<task_id>\d+)/$','do.views.task_profile'),
    (r'^do/task_prototype_profile/(?P<task_prototype_id>\d+)/$','do.views.task_prototype_profile'),
    
    
    (r'^do/own_task/(?P<task_id>\d+)/$', 'do.views.own_task'),
    (r'^do/mark_completed/(?P<task_id>\d+)/', 'do.views.mark_completed'),
    (r'^do/mark_abandoned/(?P<task_id>\d+)/', 'do.views.mark_abandoned'),
    (r'^do/post_task_message/(?P<task_id>\d+)/', 'do.views.post_task_message'),
  
    (r'^do/new_child_ajax_handler/$', 'do.views.new_child_ajax_handler'),
    
    (r'^do/list_children_as_checkbox/$', 'do.views.task_family_as_checklist_template'),
    (r'^do/get_tasks_in_tag_ajax_as_html/(?P<object_id>\d+)/', 'do.views.get_tasks_as_html', {'by_verb': False}),
    (r'^do/get_tasks_in_verb_ajax_as_html/(?P<object_id>\d+)/', 'do.views.get_tasks_as_html'), 
    
    (r'^do/protocols/$', 'do.views.protocols'),
    
    (r'^do/archives/$', 'do.views.archives'),
    
    (r'^do/get_taskBox_toot_court/(?P<task_id>\d+)/$', 'do.views.get_taskbox_toot_court'),
    
    #Power
    (r'^power/change/', 'power.views.change'),
    (r'^power/switch/', 'power.views.switch'),
    
    #Point of Sale
   # (r'^pos/autocomplete/(?P<criterion>\w+)/$', 'pos.views.autocomplete'),
    (r'^pos/beverageSale/', 'pos.views.beverageSale'),
    #(r'^pos/86product/' , 'pos.views.product86'), 
    
    #Calendar
    (r'^calendar/(?P<moon_id>\d+)/$', 'mooncalendar.views.index'), #depricated in favor of new url
    (r'^happenings/(?P<moon_name>[-\w]+)/$', 'mooncalendar.views.index'),
    
    
    (r'^moons_info', 'mooncalendar.views.moons_info'),
    
    #Events
    #(r'^booking/', 'events.views.booking'),
    #(r'^upcoming/', 'events.mooncalendar.views.upcoming'), 
    
    #Blog
    #(r'^blog/', 'blog.views.index'),
    
    #Searching
    #(r'^search/', include('haystack.urls')),
    
    #Utility
    (r'^utility/autocomplete/$', 'utility.views.autocomplete_dispatcher'),
    (r'^utility/save_tags_for_object/(?P<model_info>\w+)/$', 'utility.views.save_tags_for_object'),
    
     #Math
     (r'^donald/get_sigma/$', 'donald.views.get_sigma'),
     
     (r'^tinymce/', include('tinymce.urls')),
     
     #Mellon
     (r'^mellon/enter_new_magnetic_card/$', 'mellon.views.new_card_function_form'),
     (r'^mellon/submit_new_magnetic_card/$', 'mellon.views.save_new_card'),
     (r'^mellon/authenticate_card/$', 'mellon.views.authenticate_card'),
     
     #BlastForm
     (r'^blast_form/$', 'email_blast.views.email_blast'),
     (r'^blast_form/confirmation/$', 'email_blast.views.confirmation'),
     
)
   
urlpatterns += patterns('django.views.generic.simple',
    (r'^isLoggedInDisplay/$', 'direct_to_template', {'template': 'widgets/login.html'}),
    (r'^graph_test/', 'direct_to_template', {'template': 'graph_test.html'}),
    )

urlpatterns += patterns('',(r'^users/(?P<username>\w+)/$', 'social.views.profile'),)


handler404 = 'meta.errors.page_not_found'
handler500 = "meta.errors.server_error"
