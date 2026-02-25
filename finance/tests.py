from django.test import TestCase


class TransactionTest(TestCase):
    def setUp(self):
        self.test_transaction = {
            "amount": "1000",
            "store_name": "test",
            "category": "수입",
            "category_middle": "기타",
            "guitar": "",
            "is_confirmed": True,
            "importance": 1,
            "memo": "test",
            "is_fixed_expense": False,
            "create_at": "2026-02-25T14:09:06.250530+09:00",
            "real_date": "2026-02-25T14:09:06.250530+09:00",
        }
