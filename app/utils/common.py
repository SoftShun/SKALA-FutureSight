import os
import json
import time
from typing import Dict, List, Any, Optional
from pathlib import Path

def ensure_directories(dirs: List[str]) -> None:
    """
    필요한 디렉토리들이 존재하는지 확인하고, 없으면 생성합니다.
    
    Args:
        dirs: 확인할 디렉토리 경로 목록
    """
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)

def load_json(file_path: str) -> Dict[str, Any]:
    """
    JSON 파일을 로드합니다.
    
    Args:
        file_path: JSON 파일 경로
        
    Returns:
        Dict[str, Any]: 로드된 JSON 데이터
    """
    if not os.path.exists(file_path):
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data: Dict[str, Any], file_path: str) -> None:
    """
    데이터를 JSON 파일로 저장합니다.
    
    Args:
        data: 저장할 데이터
        file_path: 저장할 파일 경로
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_timestamp_str() -> str:
    """
    현재 시간을 기반으로 한 타임스탬프 문자열을 생성합니다.
    
    Returns:
        str: 타임스탬프 문자열 (예: "20240518_123456")
    """
    return time.strftime("%Y%m%d_%H%M%S")

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    텍스트를 최대 길이로 자릅니다.
    
    Args:
        text: 원본 텍스트
        max_length: 최대 길이
        
    Returns:
        str: 잘린 텍스트
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..." 