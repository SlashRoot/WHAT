import factory
import datetime

class PhoneNumberFactory(factory.Factory):
    type = 'mobile'
    number = factory.Sequence(lambda n: '888-555-%04.f' % n)