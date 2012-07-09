import factory
from django.contrib.auth.models import User
from people.models import Group


class UserFactory(factory.Factory):
    FACTORY_FOR = User
    
    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


    username = factory.Sequence(lambda u: "Test User %s" %  u)

class GroupFactory(factory.Factory):
    FACTORY_FOR = Group