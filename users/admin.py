from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# .models에 정의한 User 모델을 관리자 페이지에서 볼 수 있게 등록
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # 관리자 상세 페이지에서 수정할 수 있는 필드 구성
    fieldsets = UserAdmin.fieldsets + (("추가 정보", {"fields": ("role", "parent")}),)

    # 관리자 목록 페이지에서 보여줄 항목들
    list_display = ["username", "email", "role", "parent", "is_staff"]
    list_filter = ["role", "is_staff"]