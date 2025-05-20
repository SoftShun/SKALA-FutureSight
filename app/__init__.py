import os
from pathlib import Path

# 필요한 디렉토리 목록
REQUIRED_DIRS = [
    "data",
    "data/rag",
    "output"
]

# 디렉토리 생성
for directory in REQUIRED_DIRS:
    os.makedirs(directory, exist_ok=True)

# 앱 버전
__version__ = "1.0.0"
