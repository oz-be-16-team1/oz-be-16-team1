from django.contrib.auth import forms as auth_forms
from django import forms
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class CustomUserCreationForm(auth_forms.UserCreationForm):
    class Meta(auth_forms.UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role", "birth_date")  # 입력받을 필드들
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        # 필요한 추가 로직(예: 토큰 생성 등)을 여기서 처리 가능
        # 토큰 생성
        if not user.verification_token:
            user.verification_token = str(uuid.uuid4())
        if commit:
            user.save()
        return user
