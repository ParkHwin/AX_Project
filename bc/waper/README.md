# Waper 백엔드 — DB 자동 생성 API 서버

FastAPI + SQLAlchemy 기반. 서버를 켜면 `waper` 데이터베이스와 `user` / `test_image` / `result` 테이블이 **없을 때만 자동 생성**된다 (있으면 건너뛰므로 기존 데이터는 유지됨).

## 폴더 구조

```
bc/waper/
├── app/
│   ├── database.py    # DB 접속 설정 + waper DB 자동 생성 (init_database)
│   ├── models.py      # 테이블 정의 — User / TestImage / Result
│   ├── schemas.py     # API 요청/응답 형식 (비밀번호는 응답에서 제외)
│   └── main.py        # 앱 시작점 — DB/테이블 생성 실행 + API 엔드포인트
├── requirements.txt
└── .venv/             # 가상환경 (깃 무시됨)
```

## 자동 생성 동작 순서

`app/main.py`가 실행될 때:

1. `init_database()` — DB를 지정하지 않은 주소로 MySQL에 접속해 `CREATE DATABASE IF NOT EXISTS waper` 실행 (utf8mb4, 한글 지원)
2. `Base.metadata.create_all(bind=engine)` — `models.py`에 정의된 세 테이블을 `CREATE TABLE IF NOT EXISTS`로 생성
3. FastAPI 앱 시작

⚠️ `create_all()`은 **이미 있는 테이블의 구조를 바꾸지 않는다.** 컬럼을 추가/변경했다면 `ALTER TABLE`을 직접 실행하거나, 개발 초기라면 테이블을 DROP 후 재실행 (순서: result → test_image → user).

## 접속 정보

기본값은 `root / 1234 @ localhost:3306`. 환경변수로 덮어쓸 수 있다:

| 환경변수 | 기본값 |
|---|---|
| `DB_USER` | root |
| `DB_PASS` | 1234 |
| `DB_HOST` | localhost |
| `DB_PORT` | 3306 |
| `DB_NAME` | waper |

## 실행 방법

```powershell
cd bc/waper

# 최초 1회: 가상환경 생성 + 패키지 설치
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt

# 서버 실행 (MySQL이 켜져 있어야 함)
.venv\Scripts\python -m uvicorn app.main:app --port 8000 --reload
```

- API 문서(테스트 UI): http://localhost:8000/docs
- 헬스 체크: http://localhost:8000/health

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|---|---|---|
| POST | `/users/signup` | 회원가입 (`email`, `password`, `name`, `position`, `department`) — 비밀번호는 SHA-256 해시로 저장 |
| POST | `/users/login` | 로그인 (`email`, `password`) — 성공 시 회원 정보 반환 (비밀번호 제외) |
| POST | `/images?user_num=N` | 이미지 업로드 (multipart `file`) — LONGBLOB으로 저장 |
| GET | `/users/{user_num}/images` | 해당 회원의 이미지 목록 (최신순) |
| POST | `/results` | 분석 결과 저장 (`user_num`, `image_num`, `class_id1~3`, `confidence1~3`) — `class_id`는 0~8 정수 코드, `confidence`는 0~1 확률 |
| GET | `/users/{user_num}/results` | 해당 회원의 결과 목록 (최신순) |

## 프론트 연결

`main.py`에 CORS 미들웨어가 설정되어 있어 Vite dev 서버(`http://localhost:5173`)에서 바로 호출할 수 있다.

```js
// 프론트에서 호출 예시
const res = await fetch("http://localhost:8000/users/login", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ email: "...", password: "..." }),
});
```

현재 프론트(`fe/ax-app`)의 로그인/회원가입(`src/utils/auth.js`)은 localStorage 기반이라 아직 이 API를 호출하지 않는다. 연결하려면 `auth.js`의 `registerUser` / `loginUser`를 위 fetch 호출로 교체하면 된다.

## 테이블 스키마

- **user**: `user_num`(PK, 자동증가), `email`(유니크, 로그인 아이디로 사용), `pass`(해시 저장), `name`, `position`(직책), `department`(부서)
  — 프론트 회원가입 폼(성명/직책/이메일/부서/비밀번호)과 1:1 대응
- **test_image**: `image_num`(PK), `user_num`(FK→user, CASCADE), `image`(LONGBLOB), `time`(자동)
- **result**: `result_num`(PK), `user_num`(FK→user), `image_num`(FK→test_image), `class_id1~3`(SMALLINT 코드), `confidence1~3`(FLOAT 확률), `detime`(자동)

  AI 분석 결과 중 **확률이 높은 상위 3개**를 `class_id1`/`confidence1`(1위), `class_id2`/`confidence2`(2위),
  `class_id3`/`confidence3`(3위)에 저장한다. `class_id`는 AI가 출력하는 **정수 코드(0~8)**를 변환 없이
  그대로 저장한다. 코드별 의미는 **[라벨_매핑.md](라벨_매핑.md) 참고** — 주의: **8이 정상(none)이고
  0은 불량(Center)이다.** 범위 밖 값(`class_id` 0~8 외, `confidence` 0~1 외)은 API에서 422로 거부된다.
  코드→이름 해석은 DB가 아니라 프론트에서 한다.

회원 삭제 시 그 회원의 이미지·결과도 함께 삭제된다(`ondelete="CASCADE"`).

## 주의: `pass` 컬럼

`pass`는 파이썬 예약어라 코드에서는 `user.pass_`로 접근한다. 실제 DB 컬럼명만 `pass`다.
