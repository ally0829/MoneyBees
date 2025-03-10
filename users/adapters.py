# users/adapters.py
from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form=None):
        user = super().save_user(request, user, form)
        # Ensure the email is saved as the username
        if not user.username:
            user.username = user.email  # Set the username to email
            user.save()
        return user
