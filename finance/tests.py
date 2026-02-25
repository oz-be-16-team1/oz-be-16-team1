from django.test import TestCase
from rest_framework.reverse import reverse

from assets.models import Asset
from users.models import User


class TransactionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", email="", password="test")

        self.asset = Asset.objects.create(
            user=self.user, name="test통장", asset_type="bank", balance=10000
        )

    def test_create(self):
        url = reverse("finance:transaction-list")

        data = {
            "user": self.user.id,
            "asset": self.asset.id,
            "amount": "1000",
            "store_name": "test",
            "category": "income",
            "category_middle": "guitar",
            "guitar": "",
            "is_confirmed": True,
            "importance": 1,
            "memo": "test",
            "is_fixed_expense": False,
            "create_at": "2026-02-25T14:09:06.250530+09:00",
            "real_date": "2026-02-25T14:09:06.250530+09:00",
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
