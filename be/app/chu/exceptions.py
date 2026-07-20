class AIServerDownError(Exception):
    """AI 서버가 응답하지 않거나 타임아웃일 때"""
    pass


class DBServerDownError(Exception):
    """DB 서버(bc/waper)가 응답하지 않거나 저장에 실패했을 때"""
    pass


class InvalidImageFormatError(Exception):
    """지원하지 않는 확장자거나 파일이 손상됐을 때"""
    pass


class FileTooLargeError(Exception):
    """업로드 파일이 용량 제한 초과할 때"""
    pass