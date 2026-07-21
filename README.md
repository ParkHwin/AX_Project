# AX Project — 웨이퍼 불량 AI 분석 시스템

반도체 웨이퍼 맵 이미지를 업로드하면 ResNet9 딥러닝 모델이 결함 패턴을 분류하고, 결과를 대시보드와 이력으로 제공하는 풀스택 웹 애플리케이션입니다.

---

## 프로젝트 구조

```
AX_Project/
├── fe/ax-app/          # React 프론트엔드 (포트 5173)
├── be/app/             # 메인 FastAPI 백엔드 (포트 8000)
│   ├── chu/            # 이미지 업로드 · AI 연동 라우터
│   └── sg/             # 분석 이력 · 통계 · 대시보드 라우터
├── bc/waper/           # MySQL 래퍼 FastAPI (포트 8002)
│   └── app/            # 유저 · 이미지 · 결과 테이블 관리
├── ai/hero/            # ResNet9 AI 추론 서버 (포트 8001)
│   └── server.py       # /predict 엔드포인트
└── ai/hs/              # 모델 학습 코드 · 가중치 · 유틸
```

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| **Frontend** | React 18, Vite, Tailwind CSS, Recharts, Lucide React |
| **Backend** | FastAPI, SQLAlchemy, PyMySQL, Pydantic, httpx |
| **AI** | PyTorch (ResNet9), Pillow, NumPy |
| **DB** | MySQL 8.x (`waper` 데이터베이스, 자동 생성) |
| **실행 환경** | Anaconda (base), Python venv (bc/waper), Node.js |

---

## 서비스 아키텍처

```
브라우저 (5173)
    │
    ▼
Backend API (8000)
    │
    ├── POST /api/upload
    │       ├── AI Server (8001) 로 이미지 전송
    │       │       └── ResNet9 추론 결과 반환
    │       └── DB API (8002) 로 결과 저장
    │
    └── GET  /api/analyses/*
            └── DB API (8002) 조회
                        │
                    MySQL (3306)
                    waper DB
```

`be/app`은 `bc/waper`의 FastAPI 앱을 그대로 확장하여 동작합니다.
프론트엔드는 포트 8000만 호출하며, 8001과 8002는 백엔드가 내부적으로 사용합니다.

---

## 주요 기능

- **웨이퍼 이미지 업로드** — PNG 팔레트 모드, 최대 5MB, 다중 업로드 지원
- **AI 결함 분류** — 9가지 패턴 중 Top-3 확률과 함께 결과 반환
- **대시보드** — 오늘 검사 건수, 평균 불량률, AI 정확도, 시간대별·요일별 차트
- **검사 이력** — 전체 기록 페이지네이션 조회 및 정렬
- **분석 상세** — 패턴별 확률 분포 바 차트, 원본 이미지 표시
- **회원 관리** — 이메일 기반 회원가입 / 로그인

---

## 결함 클래스 (9종)

| 코드 | 클래스명 | 설명 |
|------|----------|------|
| 0 | none | 정상 (결함 없음) |
| 1 | center | 웨이퍼 중앙 집중 결함 |
| 2 | donut | 도넛형 링 패턴 결함 |
| 3 | edge-loc | 가장자리 국소 결함 |
| 4 | edge-ring | 가장자리 전체 링 결함 |
| 5 | loc | 임의 위치 국소 결함 |
| 6 | near-full | 웨이퍼 전반 결함 |
| 7 | random | 무작위 분포 결함 |
| 8 | scratch | 선형 스크래치 결함 |

---

## API 엔드포인트

### 업로드 · 분석 (be/chu)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/upload?user_num={n}` | 이미지 업로드 → AI 추론 → DB 저장 |

### 분석 이력 (be/sg)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/analyses?user_num={n}` | 분석 목록 (페이지네이션) |
| GET | `/api/analyses/{id}?user_num={n}` | 분석 상세 조회 |
| GET | `/api/analyses/dashboard?user_num={n}` | 대시보드 통계 |
| GET | `/api/analyses/statistics?user_num={n}` | 전체 통계 |
| GET | `/api/analyses/images/{image_num}` | 원본 이미지 반환 |
| PATCH | `/api/analyses/{id}?user_num={n}` | 분석 결과 수정 |
| DELETE | `/api/analyses/{id}?user_num={n}` | 분석 결과 삭제 |

### 회원 (bc/waper)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/users/signup` | 회원가입 |
| POST | `/users/login` | 로그인 |

---

## 초기 설정 (Git Pull 후)

### 1. bc/waper — 가상환경 및 환경변수

```powershell
cd bc/waper
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
```

`bc/waper/.env` 파일 생성:

```env
DB_USER=root
DB_PASS=본인_MySQL_비밀번호
DB_HOST=localhost
DB_PORT=3306
DB_NAME=waper
```

> `waper` 데이터베이스와 테이블은 서버 첫 실행 시 자동으로 생성됩니다.

### 2. be/app — 환경변수

```powershell
Copy-Item be/.env.example be/.env
```

필요 시 Anaconda base에 패키지 추가 설치:

```powershell
pip install -r be/requirements.txt
```

### 3. ai/hero — 모델 가중치 파일

아래 파일은 gitignore되어 있으므로 별도 수령 후 지정 경로에 배치합니다:

```
ai/hs/resnet9_wafer.pth
```

> 이 파일이 없으면 AI 서버가 시작 즉시 종료됩니다.

### 4. fe/ax-app — npm 패키지

```powershell
cd fe/ax-app
npm install
```

---

## 실행 방법

### VSCode (권장)

`Ctrl + Shift + B` 를 누르고 **Start All Servers** 를 선택합니다.

4개 서버가 별도 터미널에서 동시에 실행됩니다:

| 터미널 | 포트 | 역할 |
|--------|------|------|
| DB API | 8002 | MySQL 래퍼 (bc/waper) |
| AI Server | 8001 | ResNet9 추론 (ai/hero) |
| Backend | 8000 | 메인 API (be/app) |
| Frontend | 5173 | React 앱 (fe/ax-app) |

### 수동 실행

```powershell
# 1. DB API
cd bc/waper
.venv/Scripts/python -m uvicorn app.main:app --port 8002 --reload

# 2. AI 서버 (새 터미널)
$env:KMP_DUPLICATE_LIB_OK="TRUE"
cd ai/hero
C:/ProgramData/anaconda3/python.exe server.py

# 3. 백엔드 (새 터미널)
$env:PYTHONPATH="C:/절대경로/AX_Project"
cd be/app
C:/ProgramData/anaconda3/Scripts/uvicorn.exe main:app --port 8000 --reload

# 4. 프론트엔드 (새 터미널)
cd fe/ax-app
npm run dev
```

브라우저에서 `http://localhost:5173` 접속

---

## 환경변수 정리

| 파일 | 키 | 설명 |
|------|----|------|
| `bc/waper/.env` | `DB_USER`, `DB_PASS`, `DB_HOST`, `DB_PORT`, `DB_NAME` | MySQL 접속 정보 |
| `be/.env` | `AI_SERVER_URL` | AI 서버 주소 (기본: http://localhost:8001/predict) |
| `be/.env` | `DB_API_URL` | DB API 주소 (기본: http://localhost:8002) |
| `be/.env` | `MAX_UPLOAD_SIZE_MB` | 업로드 최대 용량 (기본: 5) |

---

## 체크리스트

```
[ ] Anaconda, Node.js, MySQL 설치 확인
[ ] bc/waper/.venv 생성 후 pip install -r requirements.txt
[ ] bc/waper/.env 생성 (DB_PASS 수정)
[ ] be/.env 생성 (.env.example 복사)
[ ] ai/hs/resnet9_wafer.pth 파일 배치
[ ] fe/ax-app 에서 npm install 실행
[ ] VSCode Ctrl+Shift+B 로 전체 서버 실행
[ ] http://localhost:5173 접속 확인
```
