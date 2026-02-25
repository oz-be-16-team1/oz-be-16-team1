from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Asset

User = get_user_model()


class AssetAPITest(TestCase):
    def setUp(self):
        # 모든 테스트 전에 공통으로 실행되는 준비 작업
        self.client = APIClient()

        # 테스트용 유저 두 명
        # why. 남의 자산에 접근하는 케이스도 테스트하기 위해
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", password="testpass123"
        )

        # 로그인 상태로 만들기
        self.client.force_authenticate(user=self.user)

        # 테스트용 자산 하나 미리 생성
        self.asset = Asset.objects.create(
            user=self.user,
            asset_type="bank",
            name="내 통장",
            balance=10000,
        )

    # ── 생성 테스트 ──────────────────────────────

    def test_자산_생성_성공(self):
        data = {"asset_type": "cash", "name": "용돈 지갑", "balance": 5000}
        response = self.client.post("/api/assets/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "용돈 지갑")

    def test_잔액_음수면_생성_실패(self):
        data = {"asset_type": "cash", "name": "잘못된 지갑", "balance": -1000}
        response = self.client.post("/api/assets/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_잘못된_asset_type이면_생성_실패(self):
        data = {"asset_type": "bitcoin", "name": "코인 지갑", "balance": 0}
        response = self.client.post("/api/assets/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_값을_보내도_로그인_유저로_생성됨(self):
        data = {
            "user": str(self.other_user.id),
            "asset_type": "cash",
            "name": "스푸핑 시도",
            "balance": 1000,
        }
        response = self.client.post("/api/assets/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created = Asset.objects.get(id=response.data["id"])
        self.assertEqual(created.user_id, self.user.id)

    # ── 조회 테스트 ──────────────────────────────

    def test_내_자산_목록_조회(self):
        response = self.client.get("/api/assets/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # setUp에서 1개 만들었으니 1개여야 함
        self.assertEqual(len(response.data), 1)

    def test_특정_자산_조회_성공(self):
        response = self.client.get(f"/api/assets/{self.asset.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "내 통장")

    def test_남의_자산은_조회_불가(self):
        other_asset = Asset.objects.create(
            user=self.other_user,
            asset_type="cash",
            name="남의 지갑",
            balance=99999,
        )
        response = self.client.get(f"/api/assets/{other_asset.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ── 삭제 테스트 ──────────────────────────────

    def test_자산_삭제_성공(self):
        response = self.client.delete(f"/api/assets/{self.asset.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Soft Delete라서 DB에는 남아있지만 is_active=False여야 해요
        self.asset.refresh_from_db()
        self.assertFalse(self.asset.is_active)

    def test_삭제된_자산은_목록에_안_보임(self):
        self.asset.is_active = False
        self.asset.save()
        response = self.client.get("/api/assets/")
        self.assertEqual(len(response.data), 0)

    def test_남의_자산은_삭제_불가(self):
        other_asset = Asset.objects.create(
            user=self.other_user,
            asset_type="cash",
            name="남의 지갑",
            balance=99999,
        )
        response = self.client.delete(f"/api/assets/{other_asset.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user가_없어도_str_호출_가능(self):
        self.asset.user = None
        self.asset.save(update_fields=["user"])

        rendered = str(self.asset)
        self.assertIn("deleted-user", rendered)
