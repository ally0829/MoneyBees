from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from unittest.mock import patch
from users.models import Currency  # Replace with the correct path if needed

User = get_user_model()


class AuthenticationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole TestCase"""
        #Mock exchange rate fetching prevent API calls
        patcher = patch("finance.services.fetch_exchange_rates", return_value={"GBP": 1.0})
        patcher.start()  # Start the patch
        cls.addClassCleanup(patcher.stop)  # Ensure it stops after tests run
        
        # Mock logging to prevent error messages from being printed
        patcher_log = patch("logging.getLogger")  # Patch logger's getLogger method
        mock_logger = patcher_log.start()
        mock_logger.return_value.error = patch("builtins.print").start()  # Redirect logger to print to console
        cls.addClassCleanup(patcher_log.stop)  # Ensure it stops after tests run
        
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
        """Create a test user with mocked currency to avoid API calls."""
        with patch("users.models.CustomUserManager._get_or_create_gbp_currency", return_value=None):
            self.user = User.objects.create_user(
                email='testuser@example.com',
                firstname='Test',
                lastname='User',
                password='testpassword123'
            ) 

        # Hardcode the currency value instead of fetching from profile
        gbp_currency, _ = Currency.objects.get_or_create(currency="GBP")
        self.user.currency = gbp_currency
        self.user.save()

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
        if response.status_code == 200 and 'form' in response.context:
            print("\nSignup failed. Form errors:", response.context['form'].errors)

        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, reverse('login'), fetch_redirect_response=False)

        # Ensure the new user exists in the database
        user_exists = User.objects.filter(email='newaccount@example.com').exists()
        self.assertTrue(user_exists)

    def test_user_login_valid_credentials(self):
        """Ensure a user can log in using correct credentials."""
        login_successful = self.client.login(
            email='testuser@example.com',
            password='testpassword123'
        )
        self.assertTrue(login_successful, "Manual login should succeed")

        # Log out to test the form-based login
        self.client.logout()

        response = self.client.post(reverse('login'), {
            'username': 'testuser@example.com',
            'password': 'testpassword123'
        })

        # Debugging output
        if response.status_code == 200 and hasattr(response, 'context') and 'form' in response.context:
            print("\nLogin form errors:", response.context['form'].errors)

        # Check authentication status
        response = self.client.get('/accounts/login/')
        user_auth = getattr(response.wsgi_request, 'user', None)
        self.assertTrue(user_auth and user_auth.is_authenticated, "User should be authenticated after login")

        # Verify access to a protected page
        response = self.client.get(reverse('finance:home'))
        self.assertEqual(response.status_code, 200, "Should access protected page after login")

    def test_user_login_invalid_credentials(self):
        """Ensure a user cannot log in with an incorrect password."""
        response = self.client.post(reverse('login'), {
            'username': 'testuser@example.com',
            'password': 'wrongpassword'
        })

        self.assertEqual(response.status_code, 200)  # Should not redirect
        self.assertFalse(response.wsgi_request.user.is_authenticated, "User should not be authenticated with wrong password")

    def test_user_logout(self):
        """Ensure session is cleared after user logs out."""
        login_successful = self.client.login(
            email='testuser@example.com',
            password='testpassword123'
        )
        self.assertTrue(login_successful, "Manual login should succeed")

        # Ensure user is in session
        self.assertTrue(self.client.session.get('_auth_user_id'), "User should be in session after login")

        # Test logout
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'), fetch_redirect_response=False)

        # Ensure session is cleared after logout
        self.assertFalse(self.client.session.get('_auth_user_id'), "Session should be cleared after logout")

        # Verify user is logged out
        response = self.client.get('/accounts/login/')
        self.assertFalse(getattr(response.wsgi_request, 'user', None).is_authenticated, "User should be logged out")
