from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=SocialAccount)
def update_user_profile(sender, instance, created, **kwargs):
    """
    This signal ensures that when a user signs in via Google, 
    their first name and last name are stored in the User model.
    """
    if created:  # Only run when the account is first created
        user = instance.user
        google_data = instance.extra_data  # Google API Data
        
        print("Google Data:", google_data)

        user.firstname = google_data.get('given_name', user.firstname or "Google User")
        user.lastname = google_data.get('family_name', user.lastname or "*")
        
        user.is_staff = True
        
        print(f"Updating user: {user.email}, is_staff={user.is_staff}, firstname={user.firstname}, lastname={user.lastname}")

        user.save()
