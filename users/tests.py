from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class AuthenticationTests(TestCase):
    def setUp(self):
        """set up testing environment and create a test user"""
        self.user = User.objects.create_user(
            email='testuser@example.com',
            firstname='Test',
            lastname='User',
            password='testpassword123'
        )

    def test_user_can_signup(self):
        response = self.client.post(reverse('signup'), {
            'firstname': 'Ally',
            'lastname': 'Ai',
            'email': 'newaccount@example.com',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        })

        # Debug: Print response content if test fails
        if response.status_code == 200:
            print("\nSignup failed. Form errors:",
                  response.context['form'].errors)

        # Expecting redirect to login after successful signup
        self.assertEqual(response.status_code, 302)  # ✅ Ensure it redirects
        # ✅ Redirect to login page
        self.assertRedirects(response, reverse('login'))

        # Ensure the user exists in the database
        user_exists = User.objects.filter(
            email='newaccount@example.com').exists()
        self.assertTrue(user_exists)

    def test_user_login_valid_credentials(self):
        """ensure user can login by using correct email and password"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser@example.com',
            'password': 'testpassword123'
        })

        # it should redirect to the homepage after sign in sucessfully
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('finance:home'))

        user = response.wsgi_request.user
        self.assertTrue(user.is_authenticated)

    def test_user_login_invalid_credentials(self):
        """ensure that user cannot sign in with the wrong password"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser@example.com',
            'password': 'wrongpassword'
        })

        # show the login page if login unsucessfully
        self.assertEqual(response.status_code, 200)

        # to ensure the user is not in log in status
        user = response.wsgi_request.user
        self.assertFalse(user.is_authenticated)

    def test_user_logout(self):
        """to ensure session is cleared after log out"""
        self.client.login(username='testuser@example.com',
                          password='testpassword123')
        response = self.client.get(reverse('logout'))

        # redirect to log in page after log out
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

        # to ensure user log out sucessfully
        user = response.wsgi_request.user
        self.assertFalse(user.is_authenticated)
