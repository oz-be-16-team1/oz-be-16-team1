from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse


def send_verification_email(user, request):
    # 인증토큰 없으면 생성
    if not user.verification_token:
        import uuid

        user.verification_token = str(uuid.uuid4())
        user.save()

    # 인증 링크 생성 (http://localhost:8000/api/users/verify/UUID... 형식)
    verify_url = request.build_absolute_uri(
        reverse("users:verify_email", kwargs={"token": user.verification_token})
    )

    subject = " 이메일 인증을 완료해주세요"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    # 본문 구성
    text_content = f"{user.username}님, 안녕하세요! 아래 링크를 클릭하여 가입을 완료하세요:\n\n{verify_url}"

    # 메일 객체 생성
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)

    # 한글 처리를 위해 인코딩 명시 (메일 서버 호환성용)
    msg.encoding = "utf-8"

    msg.send(fail_silently=False)
