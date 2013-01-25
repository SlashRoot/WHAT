import datetime
from haystack.indexes import RealTimeSearchIndex, CharField, EdgeNgramField

from models import Member, CommerceGroup
from django.contrib.auth.models import User


class MemberIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    name = CharField(model_attr='user')
    autocomplete_index = EdgeNgramField(use_template=True)
    short = CharField()
        
    def prepare_short(self, obj):
        return obj.user.get_full_name()
    
    def prepare_name(self, obj):
        return "%s <%s>" % (obj.user.get_full_name(), obj.user.email)

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Member.objects.all()

class PeopleIndex(RealTimeSearchIndex):
    text = EdgeNgramField(document=True, use_template=True)
    name = EdgeNgramField()
    short = CharField()
    autocomplete_index = EdgeNgramField(use_template=True)
    
    def prepare_short(self, obj):
        return obj.get_full_name()
    
    def prepare_name(self, obj):
        return "%s <%s>" % (obj.get_full_name(), obj.email)

    
    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return User.objects.all()

class CommerceGroupIndex(RealTimeSearchIndex):
    text = EdgeNgramField(document=True, use_template=True)
    autocomplete_index = EdgeNgramField(use_template=True)
    short = CharField()
    
    def prepare_short(self, obj):
        return obj.name