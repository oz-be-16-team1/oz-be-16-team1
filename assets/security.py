import base64
import hashlib
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


# Asset 식별번호(encrypted_number) 저장 규칙
# - 입력값이 이미 암호화 토큰이면 재암호화하지 않음
# - 평문이면 저장 직전에 서버에서 강제 암호화
# - 키는 SECRET_KEY 기반으로 생성해 인스턴스 내에서 일관성 유지
@lru_cache(maxsize=1)
def _get_fernet() -> Fernet:
    key_material = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
    key = base64.urlsafe_b64encode(key_material)
    return Fernet(key)


def is_encrypted(value: str) -> bool:
    """value가 현재 서버 키로 복호화 가능한 Fernet 토큰인지 확인한다."""
    if not value:
        return False
    try:
        _get_fernet().decrypt(value.encode("utf-8"))
        return True
    except (InvalidToken, ValueError, TypeError):
        return False


def encrypt_if_needed(value: str) -> str:
    """평문 입력은 암호화하고, 이미 암호화된 값은 그대로 반환한다."""
    if not value:
        return value
    if is_encrypted(value):
        return value
    return _get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")
