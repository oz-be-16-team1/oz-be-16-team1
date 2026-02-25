from rest_framework import generics, status
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .models import User
from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 이메일 인증 링크 생성 및 발송
        # 배포 시 settings에 도메인을 설정해두고 가져오기 !!!!
        verify_url = (
            f"http://localhost:8000/api/users/verify/{user.verification_token}/"
        )

        try:
            send_mail(
                subject="회원가입 이메일 인증을 완료해주세요.",
                message=f"{user.username}님, 아래 링크를 클릭하여 인증을 완료하세요.\n\n{verify_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception:
            # 이메일 발송 실패 시 처리 (로그 기록 등)
            return Response(
                {"message": "유저는 생성되었으나 인증 메일 발송에 실패했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(
            {
                "username": user.username,
                "message": "회원가입 성공! 이메일을 확인하여 인증을 완료해주세요.",
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(generics.GenericAPIView):
    """
    사용자가 이메일 링크를 클릭했을 때 호출되는 뷰
    """

    def get(self, request, token):
        try:
            user = User.objects.get(verification_token=token)
            user.is_active = True
            user.is_email_verified = True
            user.verification_token = None  # 인증 완료 후 토큰 초기화
            user.save()
            return Response(
                {"message": "이메일 인증이 완료되었습니다. 이제 로그인이 가능합니다."},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "유효하지 않은 토큰입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
