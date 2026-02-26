# 사자사자 가계부 API 스펙 v1 (요약 테이블)

작성일: 2026-02-26
기준: 현재 라우팅/뷰 구현

---

## 1. 공통 규약

### 1.1 Base URL
- 개발: `http://localhost:8000`

### 1.2 인증
- JWT Bearer
- Header: `Authorization: Bearer <access_token>`

### 1.3 공통 상태코드
- `200` 조회/수정 성공
- `201` 생성 성공
- `204` 삭제 성공
- `400` 검증 실패
- `401` 인증 실패
- `403` 권한 없음
- `404` 리소스 없음

---

## 2. Users API

주의: 현재 경로는 `config` prefix(`/api/users/`) + `users.urls` 내부 prefix(`/api/...`)가 합쳐져 ` /api/users/api/* ` 형태입니다.

| Method | Path | Auth | 설명 |
|---|---|---|---|
| POST | `/api/users/api/register/` | No | 회원가입 |
| GET | `/api/users/api/verify/{token}/` | No | 이메일 인증 완료 |
| POST | `/api/users/api/login/` | No | JWT 로그인 |
| POST | `/api/users/api/logout/` | Yes | 로그아웃(리프레시 블랙리스트) |

### Register Request
```json
{
  "username": "child01",
  "password": "pass1234",
  "email": "child@example.com",
  "role": "CHILD",
  "parent": "UUID(optional)"
}
```

### Login Response (예시)
```json
{
  "user": {
    "id": "uuid",
    "username": "child01",
    "email": "child@example.com"
  },
  "message": "로그인 성공",
  "token": {
    "access": "jwt-access",
    "refresh": "jwt-refresh"
  }
}
```

---

## 3. Assets API

| Method | Path | Auth | 설명 |
|---|---|---|---|
| GET | `/api/assets/` | Yes | 내 자산 목록 |
| POST | `/api/assets/` | Yes | 자산 생성 |
| GET | `/api/assets/{id}/` | Yes | 자산 상세 |
| PATCH | `/api/assets/{id}/` | Yes | 자산 수정(name, balance) |
| DELETE | `/api/assets/{id}/` | Yes | 자산 소프트삭제 |

### Create Request
```json
{
  "asset_type": "bank",
  "name": "저축통장",
  "provider": "KakaoBank",
  "balance": 30000,
  "display_number": "**1234",
  "encrypted_number": "raw-or-encrypted",
  "is_saving_account": true
}
```

### 주요 검증
- `asset_type` enum
- `balance >= 0`
- `name` 공백 불가

---

## 4. Finance API

## 4.1 Transaction
| Method | Path | Auth | 설명 |
|---|---|---|---|
| GET | `/api/finance/transaction/` | Yes | 거래 목록 |
| POST | `/api/finance/transaction/` | Yes | 거래 생성 |
| GET | `/api/finance/transaction/{id}/` | Yes | 거래 상세 |
| PATCH | `/api/finance/transaction/{id}/` | Yes | 거래 수정 |
| DELETE | `/api/finance/transaction/{id}/` | Yes | 거래 삭제 |

### Transaction Request (예시)
```json
{
  "asset": 1,
  "amount": "12000",
  "store_name": "스타벅스",
  "category": "spending",
  "category_middle": "choice",
  "etc": "",
  "is_confirmed": true,
  "importance": 3,
  "memo": "음료 구매",
  "is_fixed_expense": false,
  "real_date": "2026-02-25T14:09:06+09:00"
}
```

## 4.2 Fixed Expense
| Method | Path | Auth | 설명 |
|---|---|---|---|
| GET | `/api/finance/fixed/` | Yes | 정기지출 목록 |
| POST | `/api/finance/fixed/` | Yes | 정기지출 생성 |
| GET | `/api/finance/fixed/{id}/` | Yes | 정기지출 상세 |
| PATCH | `/api/finance/fixed/{id}/` | Yes | 정기지출 수정 |
| DELETE | `/api/finance/fixed/{id}/` | Yes | 정기지출 삭제 |

---

## 5. Missions API

| Method | Path | Auth | 설명 |
|---|---|---|---|
| GET | `/api/missions/` | Yes | 목표 목록 |
| POST | `/api/missions/` | Yes | 목표 생성 |
| GET | `/api/missions/{id}/` | Yes | 목표 상세 |
| PATCH | `/api/missions/{id}/` | Yes | 목표 수정 |
| DELETE | `/api/missions/{id}/` | Yes | 목표 삭제 |
| POST | `/api/missions/{id}/complete/` | Yes | 목표 완료 |
| POST | `/api/missions/{id}/cancel/` | Yes | 목표 포기 |

### Create Request
```json
{
  "title": "닌텐도 사기",
  "target_price": "50000",
  "deadline": "2026-03-01"
}
```

### Detail Response 주요 계산 필드
- `current_save_amount`
- `progress_rate`
- `days_left`

---

## 6. Contents API

## 6.1 Money Proverb
| Method | Path | Auth | 설명 |
|---|---|---|---|
| GET | `/api/contents/` | Optional | 랜덤 명언 1개 조회 |

## 6.2 Proverb Scrap
| Method | Path | Auth | 설명 |
|---|---|---|---|
| GET | `/api/contents/proverb_scrap/` | Yes | 내 스크랩 목록 |
| POST | `/api/contents/proverb_scrap/` | Yes | 스크랩 생성 |
| GET | `/api/contents/proverb_scrap/{id}/` | Yes | 스크랩 상세 |
| PATCH | `/api/contents/proverb_scrap/{id}/` | Yes | 스크랩 수정 |
| DELETE | `/api/contents/proverb_scrap/{id}/` | Yes | 스크랩 삭제 |

### Scrap Create Request
```json
{
  "proverb": 1
}
```

### 주요 검증
- 같은 사용자 기준 동일 명언 중복 스크랩 불가

---

## 7. 스키마 제약 요약

| 도메인 | 제약 |
|---|---|
| Asset | `balance >= 0` |
| Mission | `target_price >= 1`, `deadline >= today`, 진행중 1개 |
| ProverbScrap | `(user, proverb)` unique |
| Auth | 이메일 인증 전 로그인 차단 |

---

## 8. Known Gaps (v1 기준)

1. Users 경로가 `/api/users/api/*`로 중복 prefix 구조
2. 일부 엔드포인트에서 update 권한/소유권 검증 강화 필요
3. `importance`, `payment_day` 모델 레벨 범위 검증 필요
