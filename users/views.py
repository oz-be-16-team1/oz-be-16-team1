from django.contrib.auth.decorators import login_required
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from .models import User
from .forms import CustomUserCreationForm
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer
from .utils import send_verification_email


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

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
            user.delete()
            return Response(
                {"message": "인증 메일 발송에 실패하여 회원가입이 롤백되었습니다."},
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

    permission_classes = [AllowAny]

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


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        user = serializer.user
        if not user.is_email_verified:
            return Response(
                {"detail": "이메일 인증이 완료되지 않았습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 토큰 생성
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response(
            {
                "user": {"id": user.id, "username": user.username, "email": user.email},
                "message": "로그인 성공",
                "token": {
                    "access": access_token,
                    "refresh": refresh_token,
                },
            },
            status=status.HTTP_200_OK,
        )

        # 쿠키에 토큰 저장
        response.set_cookie(
            "access_token",
            access_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
        )
        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
        )

        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token") or request.COOKIES.get(
                "refresh_token"
            )
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            response = Response(
                {"message": "로그아웃 되었습니다."}, status=status.HTTP_200_OK
            )
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            return response
        except Exception:
            return Response(
                {"error": "잘못된 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST
            )


def signup(request):
    form = CustomUserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        new_user = form.save()
        send_verification_email(new_user, request)  # 가입 즉시 메일 발송

        return redirect("users:login")

    return render(request, "accounts/signup.html", {"form": form})


# 이메일 인증 링크를 클릭했을 때 처리하는 뷰
def verify_email(request, token):
    user = get_object_or_404(User, verification_token=token)
    user.is_email_verified = True
    user.save()
    return render(request, "accounts/verification_done.html")


@login_required
def resend_verification(request):
    if not request.user.is_email_verified:
        from .utils import (
            send_verification_email,
        )  # 함수 안에서 불러오거나 상단에서 import

        send_verification_email(request.user, request)
    return redirect("users:main")


@login_required  # 로그인 안 한 사람이 접근하면 로그인 페이지로 보냄
def main_home(request):
    return render(request, "accounts/main.html")
