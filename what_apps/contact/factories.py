import factory
import datetime
from what_apps.contact.models import PhoneNumber, PhoneProvider


class PhoneNumberFactory(factory.Factory):
    FACTORY_FOR = PhoneNumber
    type = 'mobile'
    number = factory.Sequence(lambda n: '888-555-%04.f' % float(n)) # Typecast required because factory_boy passes str


class PhoneServiceFactory(factory.Factory):
    FACTORY_FOR = PhoneProvider