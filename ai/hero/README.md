# Wafer Map Classification Server

이 서버는 ResNet9 AI 모델을 사용하여 웨이퍼 맵 이미지를 분류(정상/8개 불량 유형)합니다.

## 설정 (Anaconda 사용자 가이드)

Anaconda 환경을 사용하여 서버를 설정하는 권장 방법입니다.

1.  **환경 활성화:**
    터미널에서 프로젝트용 환경을 활성화하세요.
    ```bash
    conda activate <환경이름>
    ```

2.  **필수 패키지 설치:**
    필요한 라이브러리들이 설치되어 있는지 확인하세요.
    ```bash
    pip install fastapi uvicorn python-multipart torch torchvision pillow numpy opencv-python pandas requests
    ```

## 서버 실행

`AX_Project/ai/hero/` 폴더에서 아래 명령어로 서버를 바로 실행할 수 있습니다.

```bash
python server.py
```

## API 테스트

서버가 실행 중일 때, 다른 터미널에서 다음 명령어로 분류 요청을 테스트할 수 있습니다.

```bash
# curl 명령어 사용 예시
curl -X POST "http://127.0.0.1:8000/predict" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@<이미지_파일_경로>"
```
*(예: `file=@../../real_holdout_100/Center/004890_lot197_w16.png`)*
