import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken


class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("account:register")
        self.valid_payload = {
            "email": "testuser@example.com",
            "password": "StrongPass123",
            "confirm_password": "StrongPass123",
            "first_name": "Test",
            "last_name": "User",
            "role": "Job_Seeker",
        }

    def test_register_valid_user(self):
        response = self.client.post(self.url, data=self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"], self.valid_payload["email"])
        self.assertTrue(
            get_user_model().objects.filter(email=self.valid_payload["email"]).exists()
        )

    def test_register_missing_required_field(self):
        invalid_payload = self.valid_payload.copy()
        invalid_payload.pop("email")
        response = self.client.post(self.url, data=invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_duplicate_email(self):
        # Create initial user
        get_user_model().objects.create_user(
            email=self.valid_payload["email"],
            password="AnotherPass123",
            first_name="First",
            last_name="Last",
            role="Job_Seeker",
        )
        # Try to register again
        response = self.client.post(self.url, data=self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", str(response.data).lower())

    def test_register_invalid_email_format(self):
        payload = self.valid_payload.copy()
        payload["email"] = "invalid-email"
        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)


class ProfileViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="TestPassword123",
            first_name="John",
            last_name="Doe",
            role="Job_Seeker",
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("account:profile")

    def test_get_profile_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["Message"], "OK")
        self.assertEqual(response.data["Result"]["email"], self.user.email)

    def test_get_profile_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_profile_valid_data(self):
        payload = {"first_name": "Updated", "last_name": "User"}
        response = self.client.put(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["Result"]["first_name"], "Updated")

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")


class CustomLoginViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="loginuser@example.com",
            password="StrongPass123",
            first_name="Alice",
            last_name="Smith",
            role="Job_Seeker",
        )
        self.login_url = reverse("account:token_obtain_pair")

    def test_login_success_and_token_contains_custom_claims(self):
        payload = {"email": "loginuser@example.com", "password": "StrongPass123"}
        response = self.client.post(self.login_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        # Decode token and check custom claims
        access_token = response.data["access"]
        decoded = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
        self.assertEqual(decoded["email"], self.user.email)
        self.assertEqual(decoded["role"], self.user.role)
        self.assertEqual(decoded["first_name"], self.user.first_name)
        self.assertEqual(decoded["last_name"], self.user.last_name)

    def test_login_with_invalid_credentials(self):
        payload = {"email": "loginuser@example.com", "password": "WrongPassword"}
        response = self.client.post(self.login_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("No active account", str(response.data))
