import uuid
from datetime import datetime

from django.conf import settings
from rest_framework import status

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


# 사용자 인증 api 현재 승인 불가로 미사용
class OpenBankAuthURLView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        state = str(uuid.uuid4())

        auth_url = (
            f"{settings.OPEN_BANK_AUTH_URL}/oauth/2.0/authorize?"
            f"response_type=code"
            f"&client_id={settings.OPEN_BANK_CLIENT_ID}"
            f"&redirect_uri={settings.OPEN_BANK_REDIRECT_URI}"
            f"&scope=login inquiry transfer"
            f"&state={state}"
            f"&auth_type=0"
        )

        return Response({"auth_url": auth_url})


# 임의 인증 토큰 발급
class MockTokenView(APIView):
    def post(self, request):
        return Response(
            {
                "access_token": str(uuid.uuid4()),
                "refresh_token": str(uuid.uuid4()),
                "expires_in": 7776000,
                "token_type": "Bearer",
            }
        )


# Authorization 임의 검사
class MockTransactionView(APIView):
    def get(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return Response(
                {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

        return Response(
            {"rsp_code": "A0000", "rsp_message": "정상처리 되었습니다.", "res_list": []}
        )


# 오픈뱅킹 미사용으로 인해 임의 값
class MockOpenBankingTransactionView(APIView):
    def get(self, request):
        now = datetime.now()

        response_data = {
            "api_tran_id": str(uuid.uuid4()).replace("-", "")[:24],
            "api_tran_dtm": now.strftime("%Y%m%d%H%M%S"),
            "rsp_code": "A0000",
            "rsp_message": "정상처리 되었습니다.",
            "bank_tran_id": f"M{now.strftime('%Y%m%d%H%M%S')}",
            "bank_tran_date": now.strftime("%Y%m%d"),
            "bank_code_tran": "097",
            "bank_rsp_code": "000",
            "bank_rsp_message": "정상",
            "fintech_use_num": "199001234567890123456789",
            "balance_amt": "1500000",
            "res_list": [
                {
                    "tran_date": "20260225",
                    "tran_time": "153012",
                    "inout_type": "출금",
                    "tran_type": "ATM",
                    "print_content": "스타벅스",
                    "tran_amt": "12000",
                    "after_balance_amt": "1488000",
                },
                {
                    "tran_date": "20260224",
                    "tran_time": "101500",
                    "inout_type": "입금",
                    "tran_type": "급여",
                    "print_content": "월급",
                    "tran_amt": "500000",
                    "after_balance_amt": "1500000",
                },
            ],
        }

        return Response(response_data)
