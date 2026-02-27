# 사자사자 가계부 플로우차트 모음

작성일: 2026-02-27
기준: 현재 코드베이스(as-is) `users`, `assets`, `finance`, `missions`, `contents`

---

## 1) Users 인증 플로우 (회원가입/이메일인증/로그인/로그아웃)

```mermaid
flowchart TD
    A["요청 진입: /api/users/*"] --> B{"기능 선택"}

    B --> R["POST /api/users/api/register/"]
    B --> V["GET /api/users/api/verify/{token}/"]
    B --> L["POST /api/users/api/login/"]
    B --> O["POST /api/users/api/logout/"]

    R --> R1["RegisterSerializer 검증 (role/email/parent 규칙)"]
    R1 --> R2["create_user: is_active=false, verification_token(UUID)"]
    R2 --> R3{"인증 메일 발송 성공?"}
    R3 -- "아니오" --> R4["유저 삭제(롤백) 후 500 반환"]
    %% 유저 삭제(롤백)
    R3 -- "예" --> R5["201: 회원가입 성공 + 이메일 인증 안내"]

    V --> V1{"token으로 User 조회 성공?"}
    V1 -- "아니오" --> V2["400: 유효하지 않은 토큰"]
    V1 -- "예" --> V3["is_active=true, is_email_verified=true, token=None 저장"]
    V3 --> V4["200: 이메일 인증 완료"]

    L --> L1["SimpleJWT 자격 검증"]
    L1 --> L2{"아이디/비밀번호 유효?"}
    L2 -- "아니오" --> L3["401: InvalidToken"]
    L2 -- "예" --> L4{"is_email_verified == true?"}
    L4 -- "아니오" --> L5["403: 이메일 인증 필요"]
    L4 -- "예" --> L6["access/refresh 토큰 발급"]
    L6 --> L7["응답 바디 token + HttpOnly 쿠키(access_token/refresh_token) 설정"]
    L7 --> L8["200: 로그인 성공"]

    O --> O1{"Bearer access 인증됨?"}
    O1 -- "아니오" --> O2["401 Unauthorized"]
    O1 -- "예" --> O3["refresh_token을 body 또는 cookie에서 조회"]
    O3 --> O4{"refresh 존재?"}
    O4 -- "아니오" --> O7["쿠키 삭제 후 200 로그아웃"]
    O4 -- "예" --> O5{"refresh blacklist 성공?"}
    O5 -- "아니오" --> O6["400: 잘못된 토큰"]
    O5 -- "예" --> O7["쿠키 삭제 후 200 로그아웃"]
```

---

## 2) Assets 플로우

```mermaid
flowchart TD
    A["요청: /api/assets/*"] --> B{"인증됨?"}
    B -- "아니오" --> B1["401 Unauthorized"]
    B -- "예" --> C{"메서드"}

    C -- "GET /api/assets/" --> G1["Asset.objects.filter(user=request.user, is_active=true)"]
    G1 --> G2["200: 내 활성 자산 목록"]

    C -- "POST /api/assets/" --> P1["AssetSerializer 검증"]
    P1 --> P2{"name 공백/asset_type/balance 검증 통과?"}
    P2 -- "아니오" --> P3["400 ValidationError"]
    P2 -- "예" --> P4["user는 클라 입력 무시, request.user로 강제 저장"]
    P4 --> P5["encrypted_number 존재 시 save()에서 암호화"]
    P5 --> P6["201 Created (encrypted_number는 응답 제외)"]

    C -- "GET /api/assets/{id}/" --> D1["pk + user + is_active=true로 조회"]
    D1 --> D2{"존재?"}
    D2 -- "아니오" --> D3["404: 자산 없음/타인 자산/삭제 자산"]
    D2 -- "예" --> D4["200 Detail"]

    C -- "PATCH /api/assets/{id}/" --> U1["pk + user + is_active=true 조회"]
    U1 --> U2{"존재?"}
    U2 -- "아니오" --> U3["404 Not Found"]
    U2 -- "예" --> U4["AssetUpdateSerializer: name,balance만 허용"]
    U4 --> U5{"허용 외 필드 또는 유효성 오류?"}
    U5 -- "예" --> U6["400 ValidationError"]
    U5 -- "아니오" --> U7["200 Updated"]

    C -- "DELETE /api/assets/{id}/" --> X1["pk + user + is_active=true 조회"]
    X1 --> X2{"존재?"}
    X2 -- "아니오" --> X3["404 Not Found"]
    X2 -- "예" --> X4{"is_saving_account == true?"}
    X4 -- "예" --> X4a{"진행 중 미션 존재?"}
    X4a -- "예" --> X4b["400: 진행중 미션이 있어 삭제 불가"]
    X4a -- "아니오" --> X5["Soft Delete: is_active=false"]
    X4 -- "아니오" --> X5
    X5 --> X6["204 No Content"]
```

---

## 3) Finance 플로우 (Transaction + FixedExpense)

```mermaid
flowchart TD
    A["요청: /api/finance/*"] --> B{"인증됨?"}
    B -- "아니오" --> B1["401 Unauthorized"]
    B -- "예" --> R{"리소스 선택"}

    R -- "/transaction/" --> T0{"메서드"}
    T0 -- "GET list" --> T1{"요청자 role == PARENT?"}
    T1 -- "예" --> T2["본인 + 자녀(user__parent=self) 거래 조회"]
    T1 -- "아니오" --> T3["본인 거래만 조회"]
    T2 --> T4["200 List"]
    T3 --> T4

    T0 -- "GET detail" --> T5["get_queryset 범위 내 객체 조회"]
    T5 --> T6{"존재?"}
    T6 -- "아니오" --> T7["404 Not Found"]
    T6 -- "예" --> T8["SAFE_METHOD 허용 -> 200 Detail"]

    T0 -- "POST" --> T9{"asset 값 포함?"}
    T9 -- "아니오" --> T12["user=request.user로 생성"]
    T9 -- "예" --> T10["Asset(pk=asset_id, user=request.user) 조회"]
    T10 --> T11{"본인 소유 자산인가?"}
    T11 -- "아니오" --> T13["404 Not Found"]
    T11 -- "예" --> T12["user=request.user, asset=해당 자산으로 생성"]
    T12 --> T14["201 Created"]

    T0 -- "PATCH/PUT/DELETE detail" --> T15["객체 조회 후 작성자 검사"]
    T15 --> T16{"obj.user == request.user?"}
    T16 -- "아니오" --> T17["403: 수정/삭제는 작성자만 가능"]
    T16 -- "예" --> T18["수정/삭제 수행 (update 시 user 재주입)"]

    R -- "/fixed/" --> F0{"메서드"}
    F0 -- "GET list" --> F1["FixedExpense.objects.filter(user=request.user)"]
    F1 --> F2["200 List"]
    F0 -- "GET detail" --> F3["본인 queryset 기준 조회"]
    F3 --> F4{"존재?"}
    F4 -- "아니오" --> F5["404 Not Found"]
    F4 -- "예" --> F6["200 Detail"]
    F0 -- "POST" --> F7["user=request.user로 생성"]
    F7 --> F8["201 Created"]
    F0 -- "PATCH/PUT/DELETE detail" --> F9["본인 데이터만 수정/삭제 (타인 접근 시 404)"]
```

---

## 4) Missions 플로우

```mermaid
flowchart TD
    A["요청: /api/missions/*"] --> B{"인증됨?"}
    B -- "아니오" --> B1["401 Unauthorized"]
    B -- "예" --> M{"메서드"}

    M -- "GET /" --> L1["MissionGoal.objects.filter(child=request.user)"]
    L1 --> L2["MissionGoalSerializer(many=True)"]
    L2 --> L3["200 목록 (계산필드 포함)"]

    M -- "POST /" --> P1["MissionGoalCreateSerializer 검증"]
    P1 --> P2{"target_price >= 1 ?"}
    P2 -- "아니오" --> P9["400 ValidationError"]
    P2 -- "예" --> P3{"deadline >= today ?"}
    P3 -- "아니오" --> P9
    P3 -- "예" --> P4{"child의 IN_PROGRESS 존재?"}
    P4 -- "예" --> P9
    P4 -- "아니오" --> P5["child=request.user 주입 후 생성"]
    P5 --> P6["201 Created"]

    M -- "GET /{id}/" --> R1["pk + child=request.user 조회"]
    R1 --> R2{"존재?"}
    R2 -- "아니오" --> R3["404 Not Found"]
    R2 -- "예" --> R4["current_save_amount 계산"]
    R4 --> R5{"snapshot_saved_amount 존재?"}
    R5 -- "예" --> R6["snapshot 값 사용(고정)"]
    R5 -- "아니오" --> R7["활성 저축계좌(Asset) 합계 계산"]
    R6 --> R8["progress_rate, days_left 계산"]
    R7 --> R8
    R8 --> R9["200 Detail"]

    M -- "PATCH /{id}/" --> U1["pk + child=request.user 조회"]
    U1 --> U2{"존재?"}
    U2 -- "아니오" --> U3["404 Not Found"]
    U2 -- "예" --> U4["MissionGoalUpdateSerializer 검증"]
    U4 --> U5{"status == IN_PROGRESS ?"}
    U5 -- "아니오" --> U6["400 진행중 목표만 수정 가능"]
    U5 -- "예" --> U7{"target_price/deadline 유효?"}
    U7 -- "아니오" --> U8["400 ValidationError"]
    U7 -- "예" --> U9["200 Updated"]

    M -- "POST /{id}/complete/" --> C1["pk + child=request.user 조회"]
    C1 --> C2{"존재?"}
    C2 -- "아니오" --> C3["404 Not Found"]
    C2 -- "예" --> C4{"status == IN_PROGRESS ?"}
    C4 -- "아니오" --> C5["400 진행중인 목표만 완료 가능"]
    C4 -- "예" --> C6["snapshot_saved_amount=current_save_amount 저장"]
    C6 --> C7["status=COMPLETED, completed_at=now"]
    C7 --> C8["200 Completed"]

    M -- "POST /{id}/cancel/" --> X1["pk + child=request.user 조회"]
    X1 --> X2{"존재?"}
    X2 -- "아니오" --> X3["404 Not Found"]
    X2 -- "예" --> X4{"status == IN_PROGRESS ?"}
    X4 -- "아니오" --> X5["400 진행중인 목표만 포기 가능"]
    X4 -- "예" --> X6["snapshot_saved_amount=current_save_amount 저장"]
    X6 --> X7["status=CANCELLED, completed_at=now"]
    X7 --> X8["200 Cancelled"]

    M -- "DELETE /{id}/" --> D1["pk + child=request.user 조회"]
    D1 --> D2{"존재?"}
    D2 -- "아니오" --> D3["404 Not Found"]
    D2 -- "예" --> D4["Hard Delete"]
    D4 --> D5["204 No Content"]
```

---

## 5) Contents 플로우 (랜덤 명언 + 스크랩)

```mermaid
flowchart TD
    A["요청: /api/contents/*"] --> B{"리소스 선택"}

    B -- "GET /api/contents/" --> P1["MoneyProverb.objects.order_by('?').first()"]
    P1 --> P2["MoneyProverbSerializer(instance)"]
    P2 --> P3["200: 랜덤 명언 1건 (데이터 없으면 빈 객체 응답)"]

    B -- "/api/contents/proverb_scrap/*" --> S0{"인증됨?"}
    S0 -- "아니오" --> S1["401 Unauthorized"]
    S0 -- "예" --> S2{"메서드"}

    S2 -- "GET list" --> S3["ProverbScrap.objects.filter(user=request.user)"]
    S3 --> S4["200: 내 스크랩 목록"]

    S2 -- "GET detail" --> S5["내 queryset에서 단건 조회"]
    S5 --> S6{"존재?"}
    S6 -- "아니오" --> S7["404 Not Found"]
    S6 -- "예" --> S8["200 Detail"]

    S2 -- "DELETE detail" --> S9["내 queryset 대상 삭제"]
    S9 --> S10["204 No Content"]

    S2 -- "POST create" --> C1["proverb_id를 body에서 받아 조회"]
    C1 --> C2{"proverb 존재?"}
    C2 -- "아니오" --> C3["404 Not Found"]
    C2 -- "예" --> C4{"이미 스크랩했는가?"}
    C4 -- "예" --> C5["400: 이미 스크랩한 명언"]
    C4 -- "아니오" --> C6["serializer.save(user=request.user, proverb=proverb)"]
    C6 --> C7["201 Created"]
```
