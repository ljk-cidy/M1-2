import json
import os
from firebase_admin import credentials, initialize_app

# Render 환경변수에서 FIREBASE_CREDENTIALS 읽기
firebase_creds_raw = os.getenv("FIREBASE_CREDENTIALS")

if firebase_creds_raw:
    # 환경변수로 등록된 JSON 문자열 파싱
    cred_dict = json.loads(firebase_creds_raw)
    cred = credentials.Certificate(cred_dict)
else:
    # 로컬 개발 환경용 (로컬에 파일이 있는 경우)
    cred = credentials.Certificate("serviceAccountKey.json")

initialize_app(cred)