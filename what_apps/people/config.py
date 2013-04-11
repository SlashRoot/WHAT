# This file previously contained slashRoot people concepts.  These have been moved to the slashRoot app.
from what_apps.people.factories import UserFactory
from what_apps.people.models import UserProfile


def setup():
    rusty = UserFactory.create(password="password",
                              first_name="rusty",
                              last_name="spike",
                              username="rspike")
    
    rusty_profile = UserProfile.objects.create(user=rusty)
    return rusty, rusty_profile
    