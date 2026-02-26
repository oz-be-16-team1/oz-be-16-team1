from datetime import datetime

from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse

from assets.models import Asset
from finance.models import Transaction, FixedExpense
from users.models import User

"""
기능	URL name
목록 조회	list
생성	list (POST)
상세 조회	detail (GET)
수정	detail (PUT / PATCH)
삭제	detail (DELETE)
"""


# 거래내역 테스트
class TransactionTest(APITestCase):
    def setUp(self):
        # user1 부모 유저 생성
        self.user1 = User.objects.create_user(
            username="test1",
            email="test1@naver.com",
            password="test1",
            is_email_verified=True,
        )
        # user1의 자식 user2 유저 생성
        self.user2 = User.objects.create_user(
            username="test2",
            email="test2@naver.com",
            password="test2",
            role="CHILD",
            parent=self.user1,
            is_email_verified=True,
        )
        # user1의 asset1 생성
        self.asset1 = Asset.objects.create(
            user=self.user1, name="test1통장", asset_type="bank", balance=40000
        )
        # user2의 asset2 생성
        self.asset2 = Asset.objects.create(
            user=self.user2, name="test2통장", asset_type="bank", balance=50000
        )

        # 자식 거래 내역 생성
        self.transaction = Transaction.objects.create(
            user=self.user2,
            asset=self.asset2,
            amount="1000",
            store_name="test",
            category=Transaction.TransactionType.INCOME,
            category_middle=Transaction.CategoryType.ETC,
            etc="",
            is_confirmed=True,
            importance=1,
            memo="test",
            is_fixed_expense=False,
            real_date=datetime.now(),
        )

    # 정상 생성 테스트
    def test_normal_create(self):
        self.client.force_login(self.user1)
        url1 = reverse("finance:transaction-list")

        data = {
            "user": self.user1.id,
            "asset": self.asset1.id,
            "amount": "1000",
            "store_name": "test",
            "category": Transaction.TransactionType.INCOME,
            "category_middle": Transaction.CategoryType.ETC,
            "etc": "",
            "is_confirmed": True,
            "importance": 1,
            "memo": "test",
            "is_fixed_expense": False,
            "create_at": "2026-02-25T14:09:06.250530+09:00",
            "real_date": "2026-02-25T14:09:06.250530+09:00",
        }

        response = self.client.post(url1, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # 정상 조회 테스트
    def test_normal_view(self):
        # 부모 로그인
        self.client.force_login(self.user1)
        url1 = reverse("finance:transaction-list")

        response = self.client.get(url1)
        # 부모가 자식 거래 조회 가능으로 정상 조회
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 한개 생성으로 길이 1 조회
        self.assertEqual(len(response.data), 1)

        self.client.logout()
        # 자식 로그인
        self.client.force_login(self.user2)

        response = self.client.get(url1)
        # 자식은 자기 자신 거래 내역으로 정상 조회
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # 정상 상세 조회
    def test_normal_detail_view(self):
        self.client.force_login(self.user1)
        url = reverse("finance:transaction-detail", kwargs={"pk": self.transaction.id})

        response = self.client.get(url)
        # user1은 user2의 부모이며 조회 가능
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # 비정상 상세 조회 테스트
    def test_failed_view(self):
        self.user3 = User.objects.create_user(
            username="test3",
            email="test3@naver.com",
            password="test3",
            is_email_verified=True,
        )
        self.client.force_login(self.user3)
        url = reverse("finance:transaction-detail", kwargs={"pk": self.transaction.id})

        response = self.client.get(url)
        # user3은 관계가 없는 사람으로
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # 정상 수정 테스트
    def test_normal_update(self):
        self.client.force_login(self.user2)
        url = reverse("finance:transaction-detail", kwargs={"pk": self.transaction.id})

        data = {
            "memo": "test 수정",
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 수정 내용 일치 확인
        self.assertEqual(response.json()["memo"], data["memo"])

    # 비정상 수정 테스트
    def test_failed_update(self):
        self.client.force_login(self.user1)
        url = reverse("finance:transaction-detail", kwargs={"pk": self.transaction.id})

        data = {
            "memo": "test 수정",
        }
        response = self.client.patch(url, data, format="json")
        # 부모가 자식 거래 내역 수정은 불가로 실패
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    # 정상 삭제 테스트
    def test_normal_delete(self):
        self.client.force_login(self.user2)
        url = reverse("finance:transaction-detail", kwargs={"pk": self.transaction.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # 비정상 삭제 테스트
    def test_failed_delete(self):
        self.client.force_login(self.user1)
        url = reverse("finance:transaction-detail", kwargs={"pk": self.transaction.id})
        response = self.client.delete(url)

        self.assertNotEqual(response.status_code, status.HTTP_204_NO_CONTENT)


# 구독 테스트
class FixedExpenseTest(APITestCase):
    def setUp(self):
        # user1 부모 유저 생성
        self.user1 = User.objects.create_user(
            username="test1",
            email="test1@naver.com",
            password="test1",
            is_email_verified=True,
        )
        # user1의 자식 user2 유저 생성
        self.user2 = User.objects.create_user(
            username="test2",
            email="tes2@naver.com",
            password="test2",
            role="CHILD",
            parent=self.user1,
            is_email_verified=True,
        )

        # 정기 결제 등록
        self.fixed_expense = FixedExpense.objects.create(
            user=self.user1,
            title="넷플릭스",
            amount="18000",
            payment_day="10",
            category="여가",
            is_active=True,
        )

    # 정상 생성 테스트
    def test_normal_create(self):
        self.client.force_login(self.user1)
        url1 = reverse("finance:fixed-list")

        data = {
            "user": self.user1.id,
            "title": "쿠팡",
            "amount": "18000",
            "payment_day": "10",
            "category": "여가",
            "is_active": True,
        }

        response = self.client.post(url1, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # 정상 상세 조회
    def test_normal_detail_view(self):
        self.client.force_login(self.user1)
        url = reverse("finance:fixed-detail", kwargs={"pk": self.fixed_expense.id})

        response = self.client.get(url)
        # user1은 user2의 부모이며 조회 가능
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # 비정상 상세 조회 테스트
    def test_failed_view(self):
        self.client.force_login(self.user2)
        url = reverse("finance:fixed-detail", kwargs={"pk": self.fixed_expense.id})

        response = self.client.get(url)
        # user3은 관계가 없는 사람으로
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # 정상 수정 테스트
    def test_normal_update(self):
        self.client.force_login(self.user1)
        url = reverse("finance:fixed-detail", kwargs={"pk": self.fixed_expense.id})

        data = {
            "title": "test 결제",
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 수정 내용 일치 확인
        self.assertEqual(response.json()["title"], data["title"])

    # 비정상 수정 테스트
    def test_failed_update(self):
        self.client.force_login(self.user2)
        url = reverse("finance:fixed-detail", kwargs={"pk": self.fixed_expense.id})

        data = {
            "title": "test 결제",
        }
        response = self.client.patch(url, data, format="json")
        # 부모가 자식 거래 내역 수정은 불가로 실패
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    # 정상 삭제 테스트
    def test_normal_delete(self):
        self.client.force_login(self.user1)
        url = reverse("finance:fixed-detail", kwargs={"pk": self.fixed_expense.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # 비정상 삭제 테스트
    def test_failed_delete(self):
        self.client.force_login(self.user2)
        url = reverse("finance:fixed-detail", kwargs={"pk": self.fixed_expense.id})
        response = self.client.delete(url)

        self.assertNotEqual(response.status_code, status.HTTP_204_NO_CONTENT)
