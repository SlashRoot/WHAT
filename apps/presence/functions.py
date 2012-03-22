def how_user_handles_food(user):
    try:
        if user.handles_food_with_vigilance:
            return "vigilance"
    except AttributeError:
        return "probably a sucker."