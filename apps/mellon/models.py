from django.db import models

class PrivilegePrototype(models.Model):
    '''
    A type of activity, ie:
    
    "Go behind the counter...."
    '''
    name = models.CharField(max_length=80)
    
    def __unicode__(self):
        return self.name
        
class Privilege(models.Model):
    '''
    A type of activity within a particular jurisdiction, ie:
    
    "Go behind the counter at SlashRoot."
    
    An instance of a privilege as applied in a particular group (known as the jurisdiction of that privilege)
    '''
    prototype = models.ForeignKey('mellon.PrivilegePrototype')
    jurisdiction = models.ForeignKey('auth.Group', help_text="The group under which this privilege applies.")
    
    private = models.BooleanField(help_text="Only people inside the jurisdiction can see that this privilege exists.")
    very_private = models.BooleanField(help_text="Only people who have this privilege can see that it exists.")
    
    def __unicode__(self):
        return self.prototype.name + " at " + str(self.jurisdiction) #ie, "Being behind the counter at SlashRoot."
    
    def user_has(self, user):
        '''
        returns True or False for the given user
        '''
        user_has_this_privilege = True #Assume that the user has this until they fail to meet one of the bases.
        
        for basis in self.bases.all():
            if not basis.user_has(user):
                #If we come to a basis which this user does not meet, we'll set to False and break the loop.
                user_has_this_privilege = False
                break
        
        return user_has_this_privilege
    
    def list_users(self):
        '''
        Returns all users with this privilege.
        '''
        pass
    
def get_privileges_for_user(user):
    '''
    Gets all privileges for a user.
    
    For now, only works with groups.
    
    TODO: Added other priviledge bases.
    
    TODO: Rexamine and refactor.  This function can be much more efficient.  The approach of populating a list is not great.
    '''
    groups = user.groups.all()
    has_privileges = []
    
    for group in groups:
        for privilege_basis in group.privilege_bases.all():
            #We have identified a privilege basis that relies on this group.  That means that the user *might* have this privilege.  
            #We don't actually know that the user meets the basis of this group; they might need to be in this group and other groups.
            privilege = privilege_basis.privilege
            
            if privilege in has_privileges:
                break #We already tested this privilege and confirmed that they have it.
            
            if privilege.user_has(user):
                has_privileges.append(privilege)
                #We're iterating through all the *other* privilege bases of this privilege.
                
    return has_privileges            
    
    
class PrivilegeBasis(models.Model):
    privilege = models.ForeignKey('privilege', related_name="bases")
    
    def type(self):
        '''
        What type of basis is this?
        
        Return the model of the basis type (PrivilegeBasedOnGroups, etc)
        '''
        pass
    
    class Meta:
        verbose_name_plural = "Privlege Bases"
        
    def user_has(self, user):
        '''
        Awkward.  We don't know which subclass, so we're going to examine them all since there's a small number.
        
        TODO: Examine the prospect of doing this with polymorphosis.
        '''
        try:
            return self.privilegebasedongroups.user_has(user)
        except PrivilegeBasedOnGroups.DoesNotExist:
            pass
        
        try:
            return self.privilegebasedonpermission.user_has(user)
        except PrivilegeBasedOnGroups.DoesNotExist:
            pass
        
        try:
            return self.privilegebasedonbadges.user_has(user)
        except PrivilegeBasedOnGroups.DoesNotExist:
            pass
         
class PrivilegeBasedOnGroups(PrivilegeBasis):
    '''
    
    '''
    groups = models.ManyToManyField('auth.Group', related_name="privilege_bases")
    membership = models.BooleanField(default=True, help_text="True means that we're looking for membership, False means that we're looking for exile.  IE, People in the group 'Banned from this establishment' might lack a privilege that those are lack membership might have")
    
    def user_has(self, user):
        '''
        user must be a member of all groups to return True
        '''
        user_has = True #Assume they are cool unless they fail to be in one of the groups.
        
        for group in self.groups.all():
            if group in user.groups.all():
                continue
            else:
                user_has = False
                break
        return user_has
    
    class Meta:
        verbose_name_plural = "Privileges Based on Groups"
        
    def __unicode__(self):
        if self.membership:
            phrase = "In"
        else:
            phrase = "Not In"
    
        group_list_string = ""
        for group in self.groups.all():
            group_list_string += " %s," % (group)
            
            
        
        return "%s groups: %s" % (phrase, group_list_string[:-1])
    

class PrivilegeBasedOnBadges(PrivilegeBasis):
    '''
    '''
    pass

    class Meta:
            verbose_name_plural = "Privileges Based on Badges"

class PrivilegeBasedOnPermission(PrivilegeBasis):
    '''
    Based on django's permission structure from contrib.auth
    '''
    permission = models.ForeignKey('auth.Permission')
    
    class Meta:
        verbose_name_plural = "Privileges Based on Permissions"
        
class MagneticCard(models.Model):
    '''
    Magnetic card represents the plastic card whose magnetic strip contains a string which we can decode
    '''
    owner = models.OneToOneField('auth.User')
    hash = models.CharField(max_length=160)
    
    def __unicode__(self):
        return str(self.owner) + "'s card"
    
