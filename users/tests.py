from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from unittest.mock import patch

User = get_user_model()


class LoginLogoutTestCase(APITestCase):
    def setUp(self):
        # Create test user
        self.username = "testuser"
        self.email = "test@example.com"
        self.password = "password123"
        self.user = User.objects.create_user(
            username=self.username, email=self.email, password=self.password
        )

        # URL setup for API endpoints
        # Make sure these match your users/urls.py
        self.login_url = reverse("users:api_login")
        self.logout_url = reverse("users:api_logout")

    def test_login_success(self):
        """
        Test login success for verified user: checks status, tokens in body, and cookies.
        """
        self.user.is_email_verified = True
        self.user.save()

        data = {"username": self.username, "password": self.password}
        response = self.client.post(self.login_url, data)

        # 1. Check Status Code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2. Check Response Body for Tokens
        self.assertIn("token", response.data)
        self.assertIn("access", response.data["token"])
        self.assertIn("refresh", response.data["token"])
        self.assertEqual(response.data["message"], "로그인 성공")

        # 3. Check Cookies are set and HttpOnly
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        self.assertTrue(response.cookies["access_token"]["httponly"])
        self.assertTrue(response.cookies["refresh_token"]["httponly"])

    def test_login_fail_email_not_verified(self):
        """
        Test login failure when email is not verified.
        """
        self.user.is_email_verified = False
        self.user.save()

        data = {"username": self.username, "password": self.password}
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "이메일 인증이 완료되지 않았습니다.")

    def test_logout_success(self):
        """
        Test logout: checks token blacklisting and cookie deletion.
        """
        self.user.is_email_verified = True
        self.user.save()

        # 1. Login to get tokens
        login_resp = self.client.post(
            self.login_url, {"username": self.username, "password": self.password}
        )
        access_token = login_resp.data["token"]["access"]
        refresh_token = login_resp.data["token"]["refresh"]

        # 2. Logout request (Authenticated)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Send refresh token in body (simulating frontend behavior)
        data = {"refresh_token": refresh_token}
        response = self.client.post(self.logout_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "로그아웃 되었습니다.")

        # 3. Check Cookies are deleted (value is empty)
        self.assertEqual(response.cookies["access_token"].value, "")
        self.assertEqual(response.cookies["refresh_token"].value, "")

        # 4. Check Blacklist
        self.assertTrue(
            BlacklistedToken.objects.filter(token__token=refresh_token).exists(),
            "Refresh token should be blacklisted after logout",
        )

    def test_logout_invalid_token(self):
        """
        Test logout with invalid token.
        """
        self.user.is_email_verified = True
        self.user.save()

        # Generate a valid access token for auth, but send garbage refresh token
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        data = {"refresh_token": "invalid_token_string"}
        response = self.client.post(self.logout_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RegisterTestCase(APITestCase):
    def test_register_mail_fail_rolls_back_user(self):
        url = reverse("users:api_register")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "role": "PARENT",
        }

        with patch("users.views.send_mail", side_effect=Exception("mail fail")):
            response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(User.objects.filter(username="newuser").exists())
