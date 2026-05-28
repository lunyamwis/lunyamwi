from django.test import TestCase, Client
from django.urls import reverse

from .models import Signup
from .forms import EmailSignupForm


class SignupModelTest(TestCase):
    def test_str_returns_email(self):
        signup = Signup.objects.create(email="test@example.com")
        self.assertEqual(str(signup), "test@example.com")

    def test_timestamp_auto_set(self):
        signup = Signup.objects.create(email="time@example.com")
        self.assertIsNotNone(signup.timestamp)

    def test_email_uniqueness_not_enforced_at_model_level(self):
        Signup.objects.create(email="dup@example.com")
        Signup.objects.create(email="dup@example.com")
        self.assertEqual(Signup.objects.filter(email="dup@example.com").count(), 2)


class EmailSignupFormTest(TestCase):
    def test_valid_email_is_valid(self):
        form = EmailSignupForm(data={"email": "valid@example.com"})
        self.assertTrue(form.is_valid())

    def test_invalid_email_is_invalid(self):
        form = EmailSignupForm(data={"email": "not-an-email"})
        self.assertFalse(form.is_valid())

    def test_empty_email_is_invalid(self):
        form = EmailSignupForm(data={"email": ""})
        self.assertFalse(form.is_valid())


class EmailSignupViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("email-list-signup")

    def test_new_email_creates_signup(self):
        response = self.client.post(
            self.url,
            {"email": "new@example.com"},
            HTTP_REFERER="/",
        )
        self.assertEqual(Signup.objects.filter(email="new@example.com").count(), 1)

    def test_new_email_redirects_to_referer(self):
        response = self.client.post(
            self.url,
            {"email": "redirect@example.com"},
            HTTP_REFERER="/",
        )
        self.assertRedirects(response, "/", fetch_redirect_response=False)

    def test_duplicate_email_does_not_create_second_record(self):
        Signup.objects.create(email="existing@example.com")
        self.client.post(
            self.url,
            {"email": "existing@example.com"},
            HTTP_REFERER="/",
        )
        self.assertEqual(Signup.objects.filter(email="existing@example.com").count(), 1)

    def test_duplicate_email_shows_warning_message(self):
        Signup.objects.create(email="dup@example.com")
        response = self.client.post(
            self.url,
            {"email": "dup@example.com"},
            HTTP_REFERER="/",
            follow=True,
        )
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("already subscribed" in str(m) for m in messages))

    def test_invalid_email_does_not_save(self):
        self.client.post(
            self.url,
            {"email": "bad-email"},
            HTTP_REFERER="/",
        )
        self.assertEqual(Signup.objects.count(), 0)

    def test_invalid_email_shows_error_message(self):
        response = self.client.post(
            self.url,
            {"email": "notvalid"},
            HTTP_REFERER="/",
            follow=True,
        )
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("valid email" in str(m) for m in messages))

    def test_success_message_on_new_signup(self):
        response = self.client.post(
            self.url,
            {"email": "success@example.com"},
            HTTP_REFERER="/",
            follow=True,
        )
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("subscribed" in str(m).lower() for m in messages))

    def test_get_request_redirects_home(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("home"))
