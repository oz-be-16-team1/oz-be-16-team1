from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from assets.models import Asset
from .models import MissionGoal

User = get_user_model()


class MissionGoalAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # 아이 유저, 다른 유저
        self.child = User.objects.create_user(
            username="child", password="testpass123", email="test@test.com"
        )
        self.other_user = User.objects.create_user(
            username="other", password="testpass123", email="other@test.com"
        )
        self.client.force_authenticate(user=self.child)

        # 저축계좌
        self.saving_asset = Asset.objects.create(
            user=self.child,
            asset_type="bank",
            name="저축통장",
            balance=10000,
            is_saving_account=True,
        )

        # 기본 목표 데이터
        self.tomorrow = timezone.localdate() + timezone.timedelta(days=1)
        self.goal_data = {
            "title": "닌텐도 사기",
            "target_price": "50000",
            "deadline": str(self.tomorrow),
        }

        # 미리 생성된 목표
        self.goal = MissionGoal.objects.create(
            child=self.child,
            title="기존 목표",
            target_price=Decimal("30000"),
            deadline=self.tomorrow,
        )

    # ── 생성 테스트 ──────────────────────────────

    def test_목표_생성_성공(self):
        # 기존 목표 먼저 취소
        self.goal.cancel()
        response = self.client.post("/api/missions/", self.goal_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "닌텐도 사기")

    def test_활성목표_있으면_생성_실패(self):
        # 이미 IN_PROGRESS 목표가 있는 상태
        response = self.client.post("/api/missions/", self.goal_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_과거_마감일이면_생성_실패(self):
        self.goal.cancel()
        data = {**self.goal_data, "deadline": "2020-01-01"}
        response = self.client.post("/api/missions/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_목표금액_0원이면_생성_실패(self):
        self.goal.cancel()
        data = {**self.goal_data, "target_price": "0"}
        response = self.client.post("/api/missions/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_child는_로그인유저로_자동_주입(self):
        self.goal.cancel()
        response = self.client.post("/api/missions/", self.goal_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = MissionGoal.objects.get(id=response.data["id"])
        self.assertEqual(created.child, self.child)

    # ── 조회 테스트 ──────────────────────────────

    def test_목표_목록_조회(self):
        response = self.client.get("/api/missions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_목표_상세_조회(self):
        response = self.client.get(f"/api/missions/{self.goal.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "기존 목표")

    def test_남의_목표는_조회_불가(self):
        other_goal = MissionGoal.objects.create(
            child=self.other_user,
            title="남의 목표",
            target_price=Decimal("10000"),
            deadline=self.tomorrow,
        )
        response = self.client.get(f"/api/missions/{other_goal.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_current_save_amount_저축계좌_합산(self):
        response = self.client.get(f"/api/missions/{self.goal.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Decimal(response.data["current_save_amount"]), Decimal("10000")
        )

    def test_progress_rate_계산(self):
        response = self.client.get(f"/api/missions/{self.goal.id}/")
        # 10000 / 30000 * 100 = 33.3%
        self.assertEqual(response.data["progress_rate"], 33.3)

    def test_days_left_계산(self):
        response = self.client.get(f"/api/missions/{self.goal.id}/")
        self.assertEqual(response.data["days_left"], 1)

    # ── 수정 테스트 ──────────────────────────────

    def test_목표_수정_성공(self):
        response = self.client.patch(
            f"/api/missions/{self.goal.id}/",
            {"title": "수정된 목표", "target_price": "40000"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_완료된_목표는_수정_불가(self):
        self.goal.complete()
        response = self.client.patch(
            f"/api/missions/{self.goal.id}/",
            {"title": "수정 시도"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_남의_목표는_수정_불가(self):
        other_goal = MissionGoal.objects.create(
            child=self.other_user,
            title="남의 목표",
            target_price=Decimal("10000"),
            deadline=self.tomorrow,
        )
        response = self.client.patch(
            f"/api/missions/{other_goal.id}/",
            {"title": "탈취 시도"},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ── 완료/포기 테스트 ─────────────────────────

    def test_목표_완료_성공(self):
        response = self.client.post(f"/api/missions/{self.goal.id}/complete/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.goal.refresh_from_db()
        self.assertEqual(self.goal.status, MissionGoal.Status.COMPLETED)
        # 스냅샷이 저축계좌 잔액으로 저장됐는지
        self.assertEqual(self.goal.snapshot_saved_amount, Decimal("10000"))
        self.assertIsNotNone(self.goal.completed_at)

    def test_목표_포기_성공(self):
        response = self.client.post(f"/api/missions/{self.goal.id}/cancel/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.goal.refresh_from_db()
        self.assertEqual(self.goal.status, MissionGoal.Status.CANCELLED)
        self.assertIsNotNone(self.goal.snapshot_saved_amount)
        self.assertIsNotNone(self.goal.completed_at)

    def test_완료된_목표는_재완료_불가(self):
        self.goal.complete()
        response = self.client.post(f"/api/missions/{self.goal.id}/complete/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_완료후_저축계좌_잔액변경해도_스냅샷_불변(self):
        self.goal.complete()
        snapshot = self.goal.snapshot_saved_amount

        # 저축계좌 잔액 변경
        self.saving_asset.balance = Decimal("99999")
        self.saving_asset.save()

        self.goal.refresh_from_db()
        # 스냅샷은 변하지 않아야 함
        self.assertEqual(self.goal.snapshot_saved_amount, snapshot)

    # ── 삭제 테스트 ──────────────────────────────

    def test_목표_삭제_성공(self):
        response = self.client.delete(f"/api/missions/{self.goal.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(MissionGoal.objects.filter(id=self.goal.id).exists())

    def test_남의_목표는_삭제_불가(self):
        other_goal = MissionGoal.objects.create(
            child=self.other_user,
            title="남의 목표",
            target_price=Decimal("10000"),
            deadline=self.tomorrow,
        )
        response = self.client.delete(f"/api/missions/{other_goal.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
