from django.db import models
from itertools import chain

BUBBLE_ACTIONS = (
                  
                  (1, 'link'),
                  (2, 'pop'),
                  (3, 'modal'),
                  (4, 'ajax_crumb'),

                  
                  )


class Bubble(models.Model):
    url=models.CharField(max_length=300, blank=True, null=True)
    name=models.CharField(max_length=200)
    content=models.TextField(blank=True, null=True)
    action=models.IntegerField(choices=BUBBLE_ACTIONS)
    data=models.CharField(max_length=80, blank=True, null=True)
    menu_crumb=models.ForeignKey('BubbleMenu', blank=True, null=True, related_name="origins")
    
    def __unicode__(self):
        return self.name
    
#This will need to be more dynamic in the future, but I need to get something down.

class BubbleMenu(models.Model):
    bubbles=models.ManyToManyField(Bubble, related_name="menu")
    name=models.CharField(max_length=80)
    launch_name=models.CharField(max_length=80)
    crumbs=models.ManyToManyField('self', symmetrical=False, blank=True, null=True)
    
    def allBubbles(self):
        return chain(self.bubbles.all(), self.crumbs.all())
    
    def totalBubbles(self):
        return self.bubbles.count() + self.crumbs.count()
    
    def getMenuTree(self):
        #Start with an empty list
        menu_tree = []
        
        #This menu is obviously in the tree
        menu_tree.append(self)
                
        for crumb in self.crumbs.all():
            b = Bubble()
            b.url = 'javascript:;'
            b.name = crumb.name
            b.action = 2
            b.menu_crumb = crumb
            

        for new_menu in self.crumbs.all():
            
            #Avoid infinite recursion.
            if not new_menu in menu_tree:
                #Since this menu is not already in the tree, it must be added, along with all its sub-menus.
                #Thus, we'll run this very method (the one we are inside) to append them all.
                menu_tree += new_menu.getMenuTree() #Concat list to list
                
                
                    
        return menu_tree
    
    def __unicode__(self):
        return self.name