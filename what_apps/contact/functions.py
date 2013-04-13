@user_passes_test(lambda u: CUSTOMER_SERVICE.user_has(u))
def simple_phone_lookup(request):
    phone_number, created = get_or_create_nice_number(request.GET['phone_number'])
    if phone_number.owner:
        return HttpResponse(str(phone_number.owner))
    else:
        if created:
            return HttpResponse('unlogged new number')
        else:
            return HttpResponse('unlogged old number')
