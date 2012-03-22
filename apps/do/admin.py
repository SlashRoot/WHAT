#from models import Step, Project, Activity
#from django.contrib import admin
#
#
#class StepInline(admin.StackedInline):
#    model=Step.projects.through
#    
#class ProjectAdmin(admin.ModelAdmin):
#    list_display = ('name', 'projected', 'created',)
#
#    inlines =[
#              StepInline,
#              ]
#
#
#admin.site.register(Project, ProjectAdmin)
#admin.site.register(Step)
#admin.site.register(Activity)

# Create the sick choice form
#admin.site.register(Choice)

from utility.admin import autoregister

autoregister('do')