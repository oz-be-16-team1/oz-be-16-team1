# 사자사자 가계부 PRD (v0.1)

작성일: 2026-02-26

---

## 1. 제품 개요

### 1.1 제품명
- 사자사자 가계부 (부모-자녀 금융관리 서비스)

### 1.2 문제 정의
- 자녀가 용돈/지출/저축을 체계적으로 기록하고 피드백 받기 어렵다.
- 부모는 자녀의 금융 습관을 추적하고 지도할 수 있는 표준화된 데이터가 부족하다.
- 목표 저축(미션) 달성 과정이 자산 데이터와 분리되어 동기 부여가 약하다.

### 1.3 제품 목표
- 자녀의 자산/거래/정기지출/미션을 단일 시스템에서 기록/조회 가능하게 한다.
- 부모가 자녀 데이터를 조회하여 지도 가능한 구조를 제공한다.
- 미션과 저축 계좌를 연결해 목표 달성 가시성을 높인다.
- 금융 명언 스크랩으로 행동 유도형 콘텐츠 경험을 제공한다.

### 1.4 핵심 가치
- 학습: 기록 기반 금융 습관 형성
- 가시성: 부모/자녀 역할 기반 조회
- 동기부여: 미션 진행률/남은 기간/스냅샷
- 보안: 계좌 식별정보 마스킹/암호화 저장

---

## 2. 대상 사용자와 권한 모델

### 2.1 사용자 유형
- `PARENT`: 부모 계정
- `CHILD`: 자녀 계정

### 2.2 권한 정책 (도메인 레벨)
- 부모
  - 본인 거래/자산 조회 가능
  - 자녀 거래 조회 가능
  - 자녀 거래 수정/삭제는 불가
- 자녀
  - 본인 데이터 CRUD 가능
  - 타인 데이터 접근 불가

### 2.3 계정 관계
- `USER.parent_id` 자기참조 FK로 부모-자녀 관계를 표현한다.
- 부모는 여러 자녀를 가질 수 있다.

---

## 3. 정보구조(IA) 및 모듈 구조

### 3.1 Django 앱 구조
- `users`: 회원가입/인증/로그인/로그아웃, 역할/관계 관리
- `assets`: 자산(계좌/카드/현금/기프트카드) 관리
- `finance`: 거래내역, 정기지출 관리
- `missions`: 저축 목표(미션) 생성/수정/완료/포기
- `contents`: 금융 명언 조회 및 스크랩
- `config`: 설정/라우팅/Swagger

### 3.2 API 라우트 베이스
- `/api/users/`
- `/api/assets/`
- `/api/finance/`
- `/api/missions/`
- `/api/contents/`

---

## 4. 도메인 모델 (ERD 정합화)


### 4.1 USER
- 식별: `id (uuid PK)`
- 인증: `username`, `password`, `email`
- 역할: `role (PARENT|CHILD)`
- 관계: `parent_id (self FK)`
- 동의/보호: `is_verified`, `allow_monitoring`
- 이메일 인증: `is_email_verified`, `verification_token`

### 4.2 ASSET
- 사용자 소유 자산
- 유형: `asset_type (bank|card|cash|giftcard)`
- 제약: `balance >= 0`
- 식별정보 보호: `display_number(마스킹)`, `encrypted_number(암호화)`
- 저축 계좌 플래그: `is_saving_account`
- 소프트 삭제: `is_active`

### 4.3 TRANSACTION
- 거래 주체: `user_id`
- 자산 연결: `asset_id` (nullable)
- 카테고리: `category`, `category_middle`, `etc`
- 행동 피드백: `is_confirmed`, `importance`, `memo`, `ai_feedback`
- 고정비 여부: `is_fixed_expense`
- 시점: `created_at`, `real_date`

### 4.4 FIXED_EXPENSE
- 사용자 정기지출
- 핵심 필드: `title`, `amount`, `payment_day`, `category`, `is_active`

### 4.5 MISSION_GOAL
- 자녀 목표: `child_id`
- 목표값: `target_price >= 1`, `deadline >= today`
- 상태: `IN_PROGRESS | COMPLETED | CANCELLED`
- 스냅샷 정책
  - 진행중: `snapshot_saved_amount = null`, `completed_at = null`
  - 완료/포기: 두 필드 모두 `not null`

### 4.6 MONEY_PROVERB / PROVERB_SCRAP
- 명언 원본: `MONEY_PROVERB`
- 사용자 스크랩: `PROVERB_SCRAP`
- 유니크: `(user, proverb)` 중복 스크랩 방지

---

## 5. 기능 요구사항 (Functional Requirements)

## 5.1 회원/인증 (`users`)

### FR-U-001 회원가입(API)
- 사용자는 `username, password, email, role`로 가입할 수 있다.
- 이메일 인증 전 계정은 로그인 제한 상태여야 한다.

### FR-U-002 이메일 인증
- 사용자는 이메일의 인증 링크를 통해 계정을 활성화한다.
- 인증 성공 시 `is_email_verified=true` 처리한다.

### FR-U-003 로그인(API)
- JWT access/refresh 토큰을 발급한다.
- 인증 미완료 사용자는 로그인할 수 없다.

### FR-U-004 로그아웃(API)
- refresh token blacklist 처리한다.
- 인증 쿠키(access/refresh)를 제거한다.

### FR-U-005 부모-자녀 관계
- 부모 계정은 자녀 계정을 연결할 수 있어야 한다.

## 5.2 자산 (`assets`)

### FR-A-001 자산 생성
- 지원 자산 유형: `bank/card/cash/giftcard`
- `user`는 요청 사용자로 서버가 강제 주입한다.
- 잔액 음수 입력은 거부한다.

### FR-A-002 자산 목록/상세 조회
- 본인 `is_active=true` 자산만 조회한다.
- 타인 자산 조회는 허용하지 않는다.

### FR-A-003 자산 수정
- 수정 가능 필드: `name`, `balance`
- 허용 외 필드 수정은 거부한다.

### FR-A-004 자산 삭제(소프트 삭제)
- 삭제 시 물리 삭제 대신 `is_active=false`로 처리한다.

### FR-A-005 식별정보 보안
- `display_number`는 마스킹 형태를 유지한다.
- `encrypted_number`는 서버 저장 시 암호화한다.

## 5.3 거래/정기지출 (`finance`)

### FR-F-001 거래 생성
- 요청 사용자 기준으로 거래를 생성한다.
- 자산 연결 시 본인 소유 자산만 연결 가능하다.

### FR-F-002 거래 조회
- 부모: 본인 + 자녀 거래 조회 가능
- 자녀: 본인 거래만 조회 가능

### FR-F-003 거래 수정/삭제
- 작성자 본인만 수정/삭제 가능

### FR-F-004 정기지출 CRUD
- 사용자별 정기지출 CRUD 제공
- 타인 정기지출 접근은 차단

## 5.4 미션 (`missions`)

### FR-M-001 목표 생성
- 자녀는 진행중 목표를 1개만 가질 수 있다.
- 목표금액 최소 1원
- 마감일은 오늘 이후(오늘 포함)

### FR-M-002 목표 조회
- 본인 목표 목록/상세 조회 가능
- 상세 조회에 `current_save_amount, progress_rate, days_left` 계산값 포함

### FR-M-003 목표 수정
- 진행중 목표만 수정 가능
- 완료/포기 상태는 수정 불가

### FR-M-004 목표 상태 전환
- 완료: `complete()`
- 포기: `cancel()`
- 상태 전환 시 스냅샷 금액과 완료 시각을 고정 저장

### FR-M-005 목표 삭제
- 사용자 본인 목표만 삭제 가능

## 5.5 콘텐츠 (`contents`)

### FR-C-001 명언 조회
- 저장된 명언 중 랜덤 1개 조회

### FR-C-002 명언 스크랩
- 인증 사용자는 명언 스크랩 CRUD 가능
- 동일 사용자 기준 중복 스크랩 금지

---

## 6. API 요구사항 (v1)

### 6.1 Users
- `POST /api/users/api/register/`
- `GET /api/users/api/verify/{token}/`
- `POST /api/users/api/login/`
- `POST /api/users/api/logout/`

### 6.2 Assets
- `GET /api/assets/`
- `POST /api/assets/`
- `GET /api/assets/{id}/`
- `PATCH /api/assets/{id}/`
- `DELETE /api/assets/{id}/`

### 6.3 Finance
- `GET/POST /api/finance/transaction/`
- `GET/PATCH/DELETE /api/finance/transaction/{id}/`
- `GET/POST /api/finance/fixed/`
- `GET/PATCH/DELETE /api/finance/fixed/{id}/`

### 6.4 Missions
- `GET /api/missions/`
- `POST /api/missions/`
- `GET/PATCH/DELETE /api/missions/{id}/`
- `POST /api/missions/{id}/complete/`
- `POST /api/missions/{id}/cancel/`

### 6.5 Contents
- `GET /api/contents/` (랜덤 명언)
- `GET/POST /api/contents/proverb_scrap/`
- `GET/PATCH/DELETE /api/contents/proverb_scrap/{id}/`

---

## 7. 데이터/검증 규칙

### 7.1 공통
- 모든 쓰기 API는 인증 필요 (`AllowAny` 예외: 회원가입/인증/로그인)
- 타인 데이터 접근은 404 또는 권한 에러로 차단

### 7.2 필수 검증 규칙
- `Asset.balance >= 0`
- `MissionGoal.target_price >= 1`
- `MissionGoal.deadline >= today`
- `MissionGoal`: 진행중 목표 1개 제한
- `ProverbScrap`: `(user, proverb)` unique
- 이메일 인증 전 로그인 차단

---

## 8. 비기능 요구사항 (NFR)

### 8.1 보안
- JWT 인증 + refresh blacklist
- 민감 필드 서버 암호화 저장 (`encrypted_number`)
- Swagger에서 Bearer 인증 방식 제공

### 8.2 신뢰성
- 도메인 핵심 규칙은 모델 제약/검증으로 이중 보장
- 테스트 자동화: 앱별 단위/API 테스트 유지

### 8.3 성능
- 목록 조회는 기본 정렬 제공
- 관계 조회 시 `select_related` 사용(거래/스크랩 등)

### 8.4 운영
- 환경 변수 기반 설정 (`SECRET_KEY`, DB, EMAIL 등)
- 개발/운영 설정 분리

---

## 9. 성공 지표 (KPI)

### 9.1 활성도
- 주간 활성 자녀 수 (WAU)
- 사용자당 주간 거래 기록 수

### 9.2 목표 달성
- 미션 생성 대비 완료율
- 미션 평균 달성 기간

### 9.3 습관 형성
- 저축계좌 잔액 증감 추이
- 자녀 `is_confirmed` 비율

### 9.4 콘텐츠 참여
- 명언 조회수
- 명언 스크랩 전환율

---

## 10. QA 수용 기준 (Acceptance Criteria)

### AC-001 인증
- 미인증 계정 로그인 시 403 반환
- 인증 완료 후 로그인 성공 및 JWT 발급

### AC-002 자산
- 비로그인 자산 API 접근 시 401
- 타인 자산 조회/수정/삭제 불가
- 삭제 후 목록에서 제외(is_active=false)

### AC-003 거래/정기지출
- 부모는 자녀 거래 조회 가능
- 부모는 자녀 거래 수정/삭제 불가
- 정기지출은 사용자별 격리

### AC-004 미션
- 진행중 목표가 이미 있으면 신규 생성 실패
- 완료/포기 후 스냅샷 값이 고정됨
- 완료된 목표는 재완료/수정 불가

### AC-005 콘텐츠
- 랜덤 명언 조회 성공
- 동일 사용자 중복 스크랩 실패
- 다른 사용자 스크랩은 생성 가능

---

## 11. 릴리스 범위

### v1 포함
- 사용자 인증/JWT
- 자산 CRUD + 암호화 필드 저장
- 거래/정기지출 CRUD
- 미션 CRUD + 상태전환 + 진행률 계산
- 명언 조회/스크랩
- Swagger 문서

### v1 제외 (후속)
- 오픈뱅킹 실연동
- AI 피드백 자동 생성 파이프라인
- 알림/푸시
- 통계 대시보드 고도화

---
