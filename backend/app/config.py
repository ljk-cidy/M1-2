import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

# Firebase Service Account 설정
service_account_env = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

if service_account_env:
    # Production: 환경 변수 문자열에서 JSON 파싱
    cred_dict = json.loads(service_account_env)
    cred = credentials.Certificate(cred_dict)
else:
    # Local: serviceAccountKey.json 파일 사용
    cred = credentials.Certificate("serviceAccountKey.json")

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()