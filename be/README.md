# chu-backend
POST /api/upload

[요청]
Content-Type : multipart/form-data
필드명       : file
허용 형식    : png, jpg, jpeg
최대 크기    : 5MB

[응답 - 성공 200]
image_id    : string  | 이미지 식별자 (UUID)
class_id    : int     | 결함 클래스 번호 (0~8). #1,2,3 (1>2>3 순으로 확률 높은 거 )
class_name  : string  | 결함 클래스 이름
confidence  : float   | AI 예측 신뢰도 (0.0~1.0) #1,2,3 (1>2>3 순으로 확률 높은 거 )


[에러]
400 | 파일 없음 / 지원하지 않는 확장자 / 손상된 이미지
413 | 파일 크기 5MB 초과
503 | AI 서버 다운 또는 타임아웃

[현재 상태]
AI 서버 연동 전 - 목업 응답 반환 중
(class_id: 3, class_name: Edge_Ring, confidence: 0.91 고정)