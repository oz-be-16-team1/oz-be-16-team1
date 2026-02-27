from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from users.models import User
from contents.models import MoneyProverb, ProverbScrap


# 명언 출력 테스트
class MoneyProverbScrapTest(APITestCase):
    def setUp(self):
        self.money1 = MoneyProverb.objects.create(
            content="명언 내용", author="글쓴이", category="저축"
        )

    def test_normal_view(self):
        url1 = reverse("contents:proverb_list")

        response = self.client.get(url1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# 명언 관심 테스트
class ProverbScrapTest(APITestCase):
    def setUp(self):
        # user1 유저 생성
        self.user1 = User.objects.create_user(
            username="test1", email="", password="test1"
        )
        # user1의 자식 user2 유저 생성
        self.user2 = User.objects.create_user(
            username="test2",
            email="",
            password="test2",
            role="CHILD",
            parent=self.user1,
        )
        # 명언 생성
        self.money1 = MoneyProverb.objects.create(
            content="명언 내용", author="글쓴이", category="저축"
        )

        self.proverb1 = ProverbScrap.objects.create(
            user=self.user1, proverb=self.money1
        )

    # 정상 출력 테스트
    def test_normal_view(self):
        self.client.force_authenticate(user=self.user1)
        url1 = reverse("contents:proverb_scrap-list")

        response = self.client.get(url1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # 정상 관심 등록 테스트
    def test_normal_create(self):
        self.client.force_authenticate(user=self.user2)
        url1 = reverse("contents:proverb_scrap-list")

        data = {"user": self.user2.id, "proverb_id": self.money1.id}
        response = self.client.post(url1, data)
        # 다른 유저의 동일 명언 스크랩은 허용됨
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # 정상 삭제 테스트
    def test_normal_delete(self):
        self.client.force_authenticate(user=self.user1)
        url1 = reverse("contents:proverb_scrap-detail", kwargs={"pk": self.proverb1.pk})

        response = self.client.delete(url1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # 비정상 생성 테스트
    def test_failed_create(self):
        self.client.force_authenticate(user=self.user1)
        url1 = reverse("contents:proverb_scrap-list")

        data = {"user": self.user1.id, "proverb_id": self.money1.id}
        response = self.client.post(url1, data)
        # 중복 관심 등록으로 인해 400 에러
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failed_create_not_found(self):
        self.client.force_authenticate(user=self.user2)
        url1 = reverse("contents:proverb_scrap-list")

        data = {"proverb_id": 999999}
        response = self.client.post(url1, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # 비정상 삭제 테스트
    def test_failed_delete(self):
        self.client.force_authenticate(user=self.user2)
        url1 = reverse("contents:proverb_scrap-detail", kwargs={"pk": self.proverb1.pk})

        response = self.client.delete(url1)
        # 다른 유저 값을 접근으로 404 에러
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
