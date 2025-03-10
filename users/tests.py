from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

User = get_user_model()


class AuthenticationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole TestCase"""
        # Get or create the site
        site = Site.objects.get_current()
        site.domain = "127.0.0.1:8000"
        site.name = "test"
        site.save()

        # Create Google SocialApp with test credentials
        app, created = SocialApp.objects.get_or_create(
            provider="google",
            defaults={
                "name": "Google",
                "client_id": "test-client-id",
                "secret": "test-secret",
            }
        )

        # Ensure the app is associated with the site
        app.sites.clear()
        app.sites.add(site)

    def setUp(self):
        """Create a test user for authentication tests."""
        self.user = User.objects.create_user(
            email='testuser@example.com',
            firstname='Test',
            lastname='User',
            password='testpassword123'
        )

    def test_user_can_signup(self):
        """Ensure a user can successfully sign up."""
        response = self.client.post(reverse('signup'), {
            'firstname': 'Ally',
            'lastname': 'Ai',
            'email': 'newaccount@example.com',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        })

        # Debugging: Print form errors if signup fails
        if response.status_code == 200:
            print("\nSignup failed. Form errors:",
                  response.context['form'].errors)

        self.assertEqual(response.status_code, 302)  # Should redirect
        # Skip rendering the login page to avoid social login issues
        self.assertRedirects(response, reverse('login'),
                             fetch_redirect_response=False)

        # Ensure the new user exists in the database
        user_exists = User.objects.filter(
            email='newaccount@example.com').exists()
        self.assertTrue(user_exists)

    def test_user_login_valid_credentials(self):
        """Ensure a user can log in using correct credentials."""
        # First check if we can manually log in the user
        login_successful = self.client.login(
            email='testuser@example.com',
            password='testpassword123'
        )
        self.assertTrue(login_successful, "Manual login should succeed")

        # Log out to test the form-based login
        self.client.logout()

        # Use correct form field names based on error messages
        response = self.client.post(reverse('login'), {
            'username': 'testuser@example.com',  # Changed from 'login' to 'username'
            'password': 'testpassword123'
        })

        # Debugging output
        if response.status_code == 200 and hasattr(response, 'context') and 'form' in response.context:
            print("\nLogin form errors:", response.context['form'].errors)

        # Direct check for authentication status
        # Perform a request to check auth status
        response = self.client.get('/accounts/login/')
        user_auth = getattr(response.wsgi_request, 'user', None)
        self.assertTrue(user_auth and user_auth.is_authenticated,
                        "User should be authenticated after login")

        # Try accessing a protected page to verify login worked
        response = self.client.get(reverse('finance:home'))
        self.assertEqual(response.status_code, 200,
                         "Should access protected page after login")

    def test_user_login_invalid_credentials(self):
        """Ensure a user cannot log in with an incorrect password."""
        response = self.client.post(reverse('login'), {
            'username': 'testuser@example.com',  # Use correct field name
            'password': 'wrongpassword'
        })

        # If login fails, the page should not redirect (status code should be 200)
        self.assertEqual(response.status_code, 200)

        # Ensure the user remains unauthenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_user_logout(self):
        """Ensure session is cleared after user logs out."""
        # Log in the user directly
        login_successful = self.client.login(
            email='testuser@example.com',
            password='testpassword123'
        )
        self.assertTrue(login_successful, "Manual login should succeed")

        # Make sure login worked
        user_auth = self.client.session.get('_auth_user_id')
        self.assertTrue(user_auth, "User should be in session after login")

        # Test logout
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'),
                             fetch_redirect_response=False)

        # Check if session is cleared after logout
        self.assertFalse(
            self.client.session.get('_auth_user_id'),
            "Session should not contain user ID after logout"
        )

        # Since finance:home doesn't seem to be protected, we'll check if the user is authenticated
        response = self.client.get('/accounts/login/')
        self.assertFalse(
            getattr(response.wsgi_request, 'user', None).is_authenticated,
            "User should not be authenticated after logout"
        )
