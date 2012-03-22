from django.db import models
class Giraffe(object):
    def has_spots(self):
        return False


class Event(models.Model):
    pass


class Attendee(models.Model):
    event = models.ForeignKey(Event, related_name="attendees")