from random import randint

def get_username(strategy, details, user=None, *args, **kwargs):
    """
    Automatically generate a username based on email if not provided.
    """
    if user:
        return {'username': user.username}

    email = details.get('email', '')
    if email:
        username = email.split('@')[0] + str(randint(1000, 9999))  # Extract email prefix and add random number
    else:
        username = "user" + str(randint(1000, 9999))  # Fallback if email is missing

    return {'username': username}