from django.conf import urls
from django.conf import settings


from django.views.generic.base import TemplateView

from django.contrib import admin
from django.views.generic.edit import CreateView


admin.autodiscover()

urlpatterns = urls.patterns('',
    #MAIN
    (r'^$', 'what_apps.main.views.main_landing'),
    (r'^moving_2012$', 'what_apps.main.views.moving'),
    
    #CMS
    (r'^/cms/form/(?P<q_and_a_id>\d+)/$', 'what_apps.cms.views.q_and_a_form'), #Public
    (r'^hack-and-tell/$', 'what_apps.main.views.hack_and_tell'), #Public
    
    (r'^cms/edit_content_block/(?P<content_block_id>\d+)/$', 'what_apps.cms.views.edit_content_block'),
    (r'^cms/edit_content_block/$', 'what_apps.cms.views.edit_content_block'),
    
    (r'^blog/(?P<headline_slug>[-\w]+)/$', 'what_apps.cms.views.blog'), #Public
    (r'^blog/$', 'what_apps.cms.views.blog'), #Public
    
    #(r'^admin/varnish/', urls.include('varnishapp.urls')),
    
    
    
    #Accounting
    (r'^accounting/show_donations', 'what_apps.accounting.views.show_donations'),
       
    #Generic Ajax Handler - urls.include object type in URL (This is used to update objects via ajax in a generic way)
    (r'^utility/submit_generic/(?P<app_name>\w+)/(?P<object_type>\w+)/$', 'what_apps.utility.views.submit_generic'),
    (r'^utility/submit_generic_partial/(?P<object_type>\w+)/(?P<object_id>\d+)/$', 'what_apps.utility.views.submit_generic_partial'),
    
    #Commerce
    (r'^commerce/record_purchase/$', 'what_apps.commerce.views.record_purchase'),
    (r'^commerce/record_bill/$', 'what_apps.commerce.views.record_purchase', {'is_bill': True}),
    (r'^commerce/record_donation', 'what_apps.commerce.views.record_donation'),
    (r'^commerce/record_ingredient_order', 'what_apps.commerce.views.record_ingredient_order'),
    (r'^commerce/view_exchange/(?P<id>\d+)/$', 'what_apps.commerce.views.view_exchange'),
    (r'^commerce/view_purchase/(?P<seller_involvement_id>\d+)/$', 'what_apps.commerce.views.view_purchase'),
    (r'^commerce/view_pledge/(?P<pledge_id>\d+)/$', 'what_apps.commerce.views.view_pledge'),
    (r'^commerce/individual_delivery', 'what_apps.commerce.views.individual_delivery'),
    (r'^commerce/fluidbarter', 'what_apps.commerce.views.fluidbarter_main'), 
    
    #Commerce: Front-facing eshu
    (r'^eshu$', 'what_apps.commerce.views.eshu_main'),
    (r'^eshu/list_purchases/(?P<party_id>\d+)/$', 'what_apps.commerce.views.list_purchases'),

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
    (r'^admin/doc/', urls.include('django.contrib.admindocs.urls')),
    (r'^admin/', urls.include(admin.site.urls)),
    
    #Contact
    (r'^contact/contact_list', 'what_apps.contact.views.contact_list'),
    (r'^contact/contact_profile/(?P<contact_id>\d+)/', 'what_apps.contact.views.contact_profile'),
    (r'^contact/contact_profile/(?P<username>\w+)/', 'what_apps.contact.views.contact_profile'),
    (r'^contact/new_contact/', 'what_apps.contact.views.new_contact'),
    (r'contact/toggle_dial_list/(?P<dial_list_id>\d+)/', 'what_apps.contact.views.toggle_dial_list'),
    (r'contact/contact_forms_for_person/', 'what_apps.contact.views.contact_forms_for_person'),
    (r'contact/phone_number_profile/(?P<phone_number_id>\d+)/', 'what_apps.contact.views.phone_number_profile'),
    
    #Menu on TV
    (r'^bar_menu', 'what_apps.pos.views.bar_menu'),
      
    
    #Login-related views
        #Presence
    (r'^bare_login', 'what_apps.presence.views.bareLogin'), #Public
    (r'^bareLogout', 'what_apps.presence.views.bareLogout'),
    
    (r'^api/whoami/', 'what_apps.people.views.who_am_i'),
    (r'^api/remote_heartbeat_success', 'what_apps.meta.views.remote_heartbeat_success'),
    
    
    #Main
    (r'^loggedInBubbles', 'what_apps.main.views.loggedInBubbles'),
    (r'^rightSideWidgets', 'what_apps.main.views.rightSideWidgets'),
        
    
    #People
    #(r'^members/', 'people.views.members'),
    #(r'^users/(?P<username>\w+)/$', 'people.views.memberProfile'),
    #(r'^apply/', 'people.views.memberApply'),
    #(r'^curriculum/', 'people.views.memberCurriculm'), 
    (r'^people/role_form/$', 'what_apps.people.views.role_form'),
    (r'^people/awesome/$', 'what_apps.people.views.awesome_o'),
    
    #POS
    (r'^pos/pos_modal', 'what_apps.commerce.views.pos_modal'),
    #Temporary solution until better way
    (r'^pos/$', 'what_apps.pos.views.pos_landing'),
    (r'^pos/sales/$', 'what_apps.pos.views.sales'),
    
    #Presence
    (r'^presence/askPurpose', 'what_apps.presence.views.askPurpose'),
    (r'^presence/tellPurpose', 'what_apps.presence.views.tellPurpose'),
    (r'^presence/viewSessions', 'what_apps.presence.views.viewSessions'),
    (r'^presence/login', 'django.contrib.auth.views.login', {'template_name': 'presence/login_page.html'}),
    (r'^presence/close_slashroot', 'what_apps.presence.views.close_slashroot'),
    
    #hwtrack
    (r'^hwtrack/all_devices', 'what_apps.hwtrack.views.all_devices'),
    (r'^hwtrack/all_computers', 'what_apps.hwtrack.views.all_computers'),
    #(r'^service/service_check_in', 'hwtrack.views.service_check_in'),
    
    #Service
    #(r'^serviceCheckIn', 'what_apps.hwtrack.views.ServiceCheckIn'),
    (r'^computerOwner', 'what_apps.hwtrack.views.Computer_Owner'),
    #This is for a client to track their computer through the site. It will be 
    #something along these lines I suppose- AC, KP 
    #(r'^hardwareTracking', 'what_apps.hwtrack.views.hardware_Tracking')
    (r'^service/check_in/$', 'what_apps.service.views.most_basic_check_in'),
    (r'^service/the_situation/$', 'what_apps.service.views.the_situation'),
    (r'^service/archive/$', 'what_apps.service.views.archive'),
    (r'^service/tickets/(?P<service_id>\d+)/$', 'what_apps.service.views.tickets'),
    (r'^service/post_task_message/(?P<service_id>\d+)/', 'what_apps.service.views.post_task_message'),
    
    
    #Social
    (r'^social/draw_attention_ajax/', 'what_apps.social.views.draw_attention_ajax'),
    (r'^iam/$', 'what_apps.social.views.dashboard'),
    (r'^social/messages/post_top_level/(?P<object_info>\w+)/', 'what_apps.social.views.post_top_level_message'),
    (r'^social/acknowledge/(?P<attention_id>\d+)/', 'what_apps.social.views.acknowledge_notification'),
    (r'^social/log/user/(?P<username>\w+)/$', 'what_apps.social.views.log'),
    (r'^social/log/group/(?P<group_name>\w+)/$', 'what_apps.social.views.log'),
    #(r'^social/log/$', 'what_apps.social.views.log'),
    #(r'^social/log/log_landing/', 'what_apps.social.views.log')
    
    
    #Phone
    (r'^comm/', urls.include('what_apps.comm.urls')), 
    
    
    #do
    (r'^do/$', 'what_apps.do.views.landing'),
    (r'^do/big_feed/$', 'what_apps.do.views.big_feed'),
    (r'^do/public_list/$', 'what_apps.do.views.public_list'),
    (r'^do/get_people_for_verb_as_html/(?P<verb_id>\d+)/$', 'what_apps.do.views.get_people_for_verb_as_html'),
    
    (r'^do/task_form_handler', 'what_apps.do.views.task_form_handler'),
    (r'^do/create_task', 'what_apps.do.views.create_task'),
    (r'^do/task_prototype_list', 'what_apps.do.views.task_prototype_list'),

    (r'^do/task_profile/(?P<task_id>\d+)/$', 'what_apps.do.views.task_profile'),
    (r'^do/task_prototype_profile/(?P<task_prototype_id>\d+)/$', 'what_apps.do.views.task_prototype_profile'),
    
    
    (r'^do/own_task/(?P<task_id>\d+)/$', 'what_apps.do.views.own_task'),
    (r'^do/mark_completed/(?P<task_id>\d+)/', 'what_apps.do.views.mark_completed'),
    (r'^do/mark_abandoned/(?P<task_id>\d+)/', 'what_apps.do.views.mark_abandoned'),
    (r'^do/post_task_message/(?P<task_id>\d+)/', 'what_apps.do.views.post_task_message'),
  
    (r'^do/new_child_ajax_handler/$', 'what_apps.do.views.new_child_ajax_handler'),
    
    (r'^do/list_children_as_checkbox/$', 'what_apps.do.views.task_family_as_checklist_template'),
    (r'^do/get_tasks_in_tag_ajax_as_html/(?P<object_id>\d+)/', 'what_apps.do.views.get_tasks_as_html', {'by_verb': False}),
    (r'^do/get_tasks_in_verb_ajax_as_html/(?P<object_id>\d+)/', 'what_apps.do.views.get_tasks_as_html'), 
    
    (r'^do/protocols/$', 'what_apps.do.views.protocols'),
    
    (r'^do/archives/$', 'what_apps.do.views.archives'),
    
    (r'^do/get_taskBox_toot_court/(?P<task_id>\d+)/$', 'what_apps.do.views.get_taskbox_toot_court'),
    
    #Power
    (r'^power/change/', 'what_apps.power.views.change'),
    (r'^power/switch/', 'what_apps.power.views.switch'),
    
    #Point of Sale
   # (r'^pos/autocomplete/(?P<criterion>\w+)/$', 'what_apps.pos.views.autocomplete'),
    (r'^pos/beverageSale/', 'what_apps.pos.views.beverageSale'),
    #(r'^pos/86product/' , 'what_apps.pos.views.product86'), 
    
    #Calendar
    (r'^calendar/(?P<moon_id>\d+)/$', 'what_apps.mooncalendar.views.index'), #depricated in favor of new url
    (r'^happenings/(?P<moon_name>[-\w]+)/$', 'what_apps.mooncalendar.views.index'),
    
    
    (r'^moons_info', 'what_apps.mooncalendar.views.moons_info'),
    
    #Events
    #(r'^booking/', 'what_apps.events.views.booking'),
    #(r'^upcoming/', 'what_apps.events.mooncalendar.views.upcoming'), 
    
    #Blog
    #(r'^blog/', 'what_apps.blog.views.index'),
    
    #Searching
    #(r'^search/', urls.include('haystack.urls')),
    
    #Utility
    (r'^utility/autocomplete/$', 'what_apps.utility.views.autocomplete_dispatcher'),
    (r'^utility/save_tags_for_object/(?P<model_info>\w+)/$', 'what_apps.utility.views.save_tags_for_object'),
    
     #Math
     (r'^donald/get_sigma/$', 'what_apps.donald.views.get_sigma'),
     
     (r'^tinymce/', urls.include('tinymce.urls')),
     
     #Mellon
     (r'^mellon/enter_new_magnetic_card/$', 'what_apps.mellon.views.new_card_function_form'),
     (r'^mellon/submit_new_magnetic_card/$', 'what_apps.mellon.views.save_new_card'),
     (r'^mellon/authenticate_card/$', 'what_apps.mellon.views.authenticate_card'),
     
     #BlastForm
     (r'^blast_form/$', 'what_apps.email_blast.views.email_blast'),
     (r'^blast_form/confirmation/$', 'what_apps.email_blast.views.confirmation'),
     (r'^people/role_form/$', 'what_apps.people.views.role_form'),
     (r'^people/membership_roles/$', 'what_apps.people.views.membership_roles'),
    (r'^isLoggedInDisplay/$', TemplateView.as_view(), {'template': 'widgets/login.html'}),
    (r'^graph_test/', TemplateView.as_view(), {'template': 'graph_test.html'}),
)
   


urlpatterns += urls.patterns('',(r'^users/(?P<username>\w+)/$', 'what_apps.social.views.profile'),)


handler404 = 'what_apps.meta.errors.page_not_found'
handler500 = "what_apps.meta.errors.server_error"
