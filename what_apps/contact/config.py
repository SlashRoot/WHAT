from what_apps.contact.models import ContactInfo, PhoneNumber


def setup():
    rusty_contact = ContactInfo.objects.create(
      address="7 somewhere ave.",
      address_line2="apt. 69",
      city="New Paltz",
      state="New York",
      postal_code=12561
    )
    
    home_number = PhoneNumber.objects.create(number=8455556669,
                                             owner=rusty_contact,
                                             type="home")
    work_number = PhoneNumber.objects.create(number=8455559996,
                                             owner=rusty_contact,
                                             type="work")
    
    return rusty_contact, home_number, work_number
    
    