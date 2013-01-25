import factory
from django.contrib.auth.models import User
from models import UserProfile

class UserFactory(factory.Factory):
    FACTORY_FOR = User
    
    @classmethod
    def _prepare(klass, create, password=None, **kwargs):
        password = password
        user = super(UserFactory, klass)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


    username = factory.Sequence(lambda u: "user %s" %  u)
