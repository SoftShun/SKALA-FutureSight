import os
import json
import shutil
from typing import List, Dict, Any, Optional
from pathlib import Path

# 지원되는 문서 타입
SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.txt', '.md']
# 최대 문서 수
MAX_DOCUMENTS = 2
# RAG 문서 저장 경로
RAG_DIR = Path("data/rag")


class DocumentManager:
    """RAG에 사용될 문서를 관리하는 클래스"""
    
    def __init__(self):
        """DocumentManager 초기화"""
        self.rag_dir = RAG_DIR
        os.makedirs(self.rag_dir, exist_ok=True)
        self.metadata_file = self.rag_dir / "metadata.json"
        self._init_metadata()
    
    def _init_metadata(self):
        """메타데이터 파일을 초기화합니다."""
        if not self.metadata_file.exists():
            self._save_metadata({
                "documents": []
            })
    
    def _load_metadata(self) -> Dict[str, Any]:
        """메타데이터를 로드합니다."""
        if not self.metadata_file.exists():
            return {"documents": []}
        
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_metadata(self, metadata: Dict[str, Any]):
        """메타데이터를 저장합니다."""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def list_documents(self) -> List[str]:
        """등록된 문서 목록을 반환합니다."""
        metadata = self._load_metadata()
        return metadata.get("documents", [])
    
    def add_document(self, file_path: str) -> bool:
        """
        문서를 RAG 시스템에 추가합니다.
        
        Args:
            file_path: 추가할 문서의 경로
            
        Returns:
            bool: 성공 여부
            
        Raises:
            ValueError: 지원되지 않는 파일 형식이거나 최대 문서 수를 초과한 경우
        """
        file_path = Path(file_path)
        
        # 파일 존재 확인
        if not file_path.exists():
            raise ValueError(f"파일을 찾을 수 없습니다: {file_path}")
        
        # 파일 형식 확인
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"지원되지 않는 파일 형식입니다. 지원 형식: {', '.join(SUPPORTED_EXTENSIONS)}")
        
        # 문서 수 제한 확인
        metadata = self._load_metadata()
        if len(metadata["documents"]) >= MAX_DOCUMENTS:
            raise ValueError(f"최대 {MAX_DOCUMENTS}개의 문서만 등록할 수 있습니다.")
        
        # 파일 페이지 수 확인 (30페이지 이내로 제한)
        # 실제 구현에서는 다양한 파일 형식에 대한 페이지 수 검증 로직 추가
        
        # 문서 복사
        destination = self.rag_dir / file_path.name
        shutil.copy2(file_path, destination)
        
        # 메타데이터 업데이트
        if str(destination) not in metadata["documents"]:
            metadata["documents"].append(str(destination))
            self._save_metadata(metadata)
        
        return True
    
    def delete_document(self, file_path: str) -> bool:
        """
        문서를 RAG 시스템에서 삭제합니다.
        
        Args:
            file_path: 삭제할 문서의 경로
            
        Returns:
            bool: 성공 여부
        """
        file_path = str(file_path)  # Path 객체를 문자열로 변환
        
        # 메타데이터에서 제거
        metadata = self._load_metadata()
        if file_path in metadata["documents"]:
            metadata["documents"].remove(file_path)
            self._save_metadata(metadata)
        
        # 실제 파일 삭제
        if Path(file_path).exists():
            os.remove(file_path)
        
        return True
    
    def get_document_content(self, file_path: str) -> str:
        """
        문서의 내용을 추출합니다. 실제 구현에서는 파일 형식에 따라 다른 추출 로직 사용
        
        Args:
            file_path: 문서 경로
            
        Returns:
            str: 추출된 문서 내용
        """
        # 간단한 구현, 실제로는 파일 형식에 따라 다른 파서 사용 필요
        file_path = Path(file_path)
        
        # 텍스트 파일 처리
        if file_path.suffix.lower() in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        # PDF, DOCX 등 다른 형식은 실제 구현에서 추가 필요
        # 예: PDF -> PyPDF2, DOCX -> python-docx 등 사용
        
        return "문서 내용 추출 미구현"  # 실제 구현에서는 파일 내용 반환 