---

# 📊 내 데이터 기반 맞춤형 AI 비서 서비스 (Data-Aware AI Assistant)

## 1. 서비스 소개

사용자의 시계열 데이터(개인 학습 시간 기록)를 **Firebase Firestore**에 저장하고 실시간으로 분석합니다. 분석된 통계 데이터 요약(Context)을 **OpenAI GPT 모델**의 시스템 프롬프트에 동적으로 주입(Context Injection)하여, AI가 사용자의 실제 상태와 수치를 명확히 파악하고 맞춤형 답변을 제공하는 지능형 웹 서비스입니다.

---

## 2. 주요 기능

* **데이터 기반 AI 맞춤형 대화**: 시계열 분석 요약 정보를 시스템 프롬프트에 주입하여 실제 데이터 수치에 기반한 답변 제공
* **시계열 데이터 관리 (CRUD)**: 학습 기록 데이터 추가, 목록 조회, 수정, 삭제 기능 및 실시간 반영
* **대화 기록 저장 및 복원**: 이전 대화 목록을 Firestore에 자동 저장하고, 선택 시 과거 대화 흐름 복원
* **인사이트 및 시각화 (보너스)**: Chart.js 기반 추세 그래프 제공, 표준편차 및 최근 7일 평균 지표 확장
* **데이터 내보내기 & UI 편의성 (보너스)**: 시계열 데이터 CSV 다운로드 기능 및 다크 모드 토글 지원
* **AI 도구 호출 (Function Calling, 보너스)**: GPT 모델이 필요한 순간 백엔드의 데이터 요약 함수를 직접 호출하도록 구현

---

## 3. 기술 스택

| 구분 | 기술 스택 |
| --- | --- |
| **Backend** | Python 3.10+, FastAPI, Pydantic, Firebase Admin SDK, OpenAI SDK |
| **Database** | Firebase Firestore |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript, Chart.js |
| **Deployment** | Render (Backend API), Vercel (Frontend Web) |
| **Tools/VCS** | Git, GitHub, VS Code, Swagger UI |

---

## 4. 배포 URL 및 API 문서

* **Frontend App**: `[https://your-project.vercel.app](https://your-project.vercel.app)` *(실제 Vercel 배포 주소로 변경)*
* **Backend API**: `[https://your-project.onrender.com](https://your-project.onrender.com)` *(실제 Render 배포 주소로 변경)*
* **Swagger API Docs**: `[https://your-project.onrender.com/docs](https://your-project.onrender.com/docs)`

---

## 5. 환경 변수 목록 (Environment Variables)

### Backend (`.env` & Render Environment)

```env
OPENAI_API_KEY="sk-proj-..."
FIREBASE_SERVICE_ACCOUNT_JSON="{\"type\": \"service_account\", \"project_id\": \"...\", ...}"
ALLOWED_ORIGINS="*"

```

---

## 6. 로컬 실행 방법

### 1) 프로젝트 클론 및 이동

```bash
git clone https://github.com/본인_아이디/프로젝트명.git
cd 프로젝트명/backend

```

### 2) 가상환경 생성 및 활성화

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

```

### 3) 의존성 라이브러리 설치

```bash
pip install -r requirements.txt

```

### 4) 백엔드 개발 서버 구동

```bash
uvicorn app.main:app --reload

```

* 서버 구동 확인: `[http://127.0.0.1:8000](http://127.0.0.1:8000)`
* Swagger UI 접속: `[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)`

### 5) 프론트엔드 실행

`frontend/index.html` 파일을 웹 브라우저로 열거나, VS Code의 Live Server 확장을 통해 구동합니다.

---

## 7. 제출 스크린샷

### 1) 데이터 요약 및 AI 채팅 화면

> 상단 요약 카드 수치(기간, 총 개수, 평균값 등)와 AI가 데이터 통계를 인용하여 작성한 답변 화면
> 

### 2) 데이터 관리 (CRUD) 화면

> 새로운 시계열 데이터 추가 입력 폼 및 아래 표(Table)에 추가/삭제된 데이터 반영 모습
> 

### 3) 대화 기록 불러오기 화면

> 사이드바에서 이전 대화 목록을 선택했을 때 과거 대화 내용이 중앙 채팅창에 재표시되는 화면
> 

---

## 🌟 8. 보너스 과제 구현 내용

### 1. 인사이트·UX 고도화

* **추가 통계 지표 제공**: 기존 기본 통계(합계, 평균, 최고/최저)에 더해 **표준편차(`std_dev`)** 및 **최근 7일 평균(`recent_7d_avg`)** 지표를 추가 분석하여 제공
* **시계열 데이터 시각화**: Chart.js 라이브러리를 연동해 날짜별 수치 변화 추세를 직관적인 선 그래프(Line Chart)로 시각화
* **데이터 내보내기**: Firestore에 저장된 데이터를 클라이언트 단에서 CSV 파일로 즉시 다운로드하는 기능 탑재
* **다크 모드 지원**: 사용자 시력 보호 및 UX 향상을 위해 상단 다크 모드 토글 기능 구현

### 2. AI 도구 호출 (Function Calling) 프로세스

#### [호출 근거]

사용자가 데이터의 최신 수치나 통계 요약을 질문할 때, GPT 모델이 임의의 환각(Hallucination) 답변을 생성하지 않고 정밀한 DB 계산 결과를 가져오도록 `get_data_summary` 도구 호출을 유도합니다.

#### [호출 흐름도]

```text
[User] "내 최근 데이터 추세랑 평균이 어떻게 돼?"
   │
   ▼
[GPT Model] 질문 분석 후 도구 호출 필요성 판단 ──> Tool Call: get_data_summary() 요청
   │
   ▼
[FastAPI Backend] Firestore 데이터 수집 및 analyzer.py를 통해 통계 지표 계산
   │
   ▼
[GPT Model] 계산된 JSON 결과를 전달받아 자연어 답변 구성
   │
   ▼
[User] "현재 총 100개 데이터 기준 평균은 3.8시간이며, 최근 상승 추세입니다."

```

---

## 9. 과제 목표 핵심 개념 요약

* **시계열 데이터 요약 흐름**: Firestore에 누적된 시계열 데이터 전체를 불러와 정렬 후 평균, 최고/최저, 정규화 추세 등을 계산하여 JSON 형태의 요약 지표로 변환합니다.
* **FastAPI 구조 분리**: `main.py`(앱 초기화/CORS), `routers/`(엔드포인트), `models.py`(Pydantic 검증), `services/`(비즈니스 로직 및 외부 SDK)로 모듈화하여 가독성과 유지보수성을 극대화했습니다.
* **Pydantic 데이터 검증**: HTTP 요청 데이터의 타입과 필드를 런타임에서 자동으로 검증하여 데이터 무결성을 보장하고 무효한 데이터 저장을 방지합니다.
* **Firestore CRUD**: NoSQL 컬렉션 구조(`data`, `conversations`)를 기반으로 Document 레벨에서 데이터 생성, 조회, 수정, 삭제를 손쉽게 처리합니다.
* **컨텍스트 주입 (Context Injection)**: 사용자의 질문 전달 전, System Prompt 내에 데이터 요약 텍스트를 결합하여 GPT 모델이 사용자의 구체적인 맥락을 학습하도록 유도합니다.
* **CORS 및 보안 기본**: CORS 미들웨어를 통해 허용된 프론트엔드 도메인 통신만 허용하고, API Key 및 서비스 계정 키는 `.env` 및 클라우드 환경 변수로 안전하게 격리 관리합니다.
