# chu-backend
POST /api/upload

[요청]
Content-Type : multipart/form-data
쿼리 파라미터 : user_num (int, 필수) — bc/waper에 저장할 회원 번호
필드명       : file
허용 형식    : png, jpg, jpeg
최대 크기    : 5MB

[응답 - 성공 200]
image_id    : string  | 이미지 식별자 (UUID)
class_id    : int     | 결함 클래스 번호 (0~8). #1,2,3 (1>2>3 순으로 확률 높은 거 )
class_name  : string  | 결함 클래스 이름
confidence  : float   | AI 예측 신뢰도 (0.0~1.0) #1,2,3 (1>2>3 순으로 확률 높은 거 )

예시:
{
  "image_id":   "550e8400-e29b-41d4-a716-446655440000",
  "class_id":   [3, 1, 5],
  "class_name": ["Edge_Ring", "Center", "Scratch"],
  "confidence": [0.91, 0.06, 0.02]
}

[에러]
400 | 파일 없음 / 지원하지 않는 확장자 / 손상된 이미지
413 | 파일 크기 5MB 초과
503 | AI 서버 다운/타임아웃 또는 DB 서버 저장 실패

[현재 상태]
AI 서버 연동 전 - 목업 응답 반환 중
(class_id: 3, class_name: Edge_Ring, confidence: 0.91 고정)

AI 예측 후 bc/waper(DB)에 이미지 + 상위 3개 결과(class_id1~3, confidence1~3)를
자동으로 저장한다. 주소는 .env의 DB_API_URL로 설정 (기본값 http://localhost:8001,
AI 서버가 8000을 쓰므로 겹치지 않게 8001에서 bc/waper를 실행해야 함).