import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

# Render 환경변수 또는 로컬 키 파일 읽기
service_account_env = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

if service_account_env:
    # Render 배포 환경: 문자열 형태의 JSON 파싱
    cred_dict = json.loads(service_account_env)
    cred = credentials.Certificate(cred_dict)
else:
    # 로컬 개발 환경: 키 파일 읽기 (파일이 없으면 임시 예외 처리)
    key_path = os.path.join(os.path.dirname(__file__), "../../serviceAccountKey.json")
    if os.path.exists(key_path):
        cred = credentials.Certificate(key_path)
    else:
        cred = None

if cred and not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# db 변수 정의 (Firestore 클라이언트)
db = firestore.client() if cred else None