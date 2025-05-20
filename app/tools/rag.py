import os
import tempfile
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredMarkdownLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma  # langchain_chroma에서 직접 임포트
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

class RAGSystem:
    """
    RAG(Retrieval-Augmented Generation) 시스템.
    사용자 제공 문서를 처리하여, 관련 정보를 검색할 수 있게 합니다.
    """
    
    def __init__(self, documents: List[str] = None):
        """
        RAG 시스템 초기화
        
        Args:
            documents: 처리할 문서 경로 목록
        """
        self.documents = documents or []
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = None
        
        # Chroma DB를 저장할 디렉토리 설정
        self.persist_directory = os.path.join(os.getcwd(), "data", "chroma_db")
        os.makedirs(self.persist_directory, exist_ok=True)
        
        self._initialize()
    
    def _initialize(self):
        """문서를 로드하고 벡터 저장소를 초기화합니다."""
        if not self.documents:
            return
        
        all_docs = []
        for doc_path in self.documents:
            all_docs.extend(self._load_document(doc_path))
        
        if all_docs:
            chunks = self.text_splitter.split_documents(all_docs)
            self.vectorstore = Chroma.from_documents(
                documents=chunks, 
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            # langchain_chroma는 자동으로 persist() 처리하므로 별도 호출 필요 없음
    
    def _load_document(self, file_path: str) -> List[Document]:
        """
        파일 형식에 맞는 로더를 사용하여 문서를 로드합니다.
        
        Args:
            file_path: 문서 경로
            
        Returns:
            List[Document]: 로드된 문서 객체 목록
        """
        path = Path(file_path)
        
        try:
            if path.suffix.lower() == '.pdf':
                loader = PyPDFLoader(str(path))
            elif path.suffix.lower() == '.docx':
                loader = Docx2txtLoader(str(path))
            elif path.suffix.lower() == '.txt':
                loader = TextLoader(str(path))
            elif path.suffix.lower() == '.md':
                loader = UnstructuredMarkdownLoader(str(path))
            else:
                return []
            
            return loader.load()
        except Exception as e:
            print(f"문서 로드 중 오류 발생: {str(e)}")
            return []
    
    def query(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        질의와 관련된 문서 청크를 검색합니다.
        
        Args:
            query: 검색 질의
            top_k: 반환할 최대 결과 수
            
        Returns:
            List[Dict[str, Any]]: 검색 결과 목록 (문서 내용, 메타데이터, 유사도 점수 포함)
        """
        if not self.vectorstore:
            return []
        
        results = self.vectorstore.similarity_search_with_score(query, k=top_k)
        
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)
            })
        
        return formatted_results
    
    def get_context_for_prompt(self, query: str, max_tokens: int = 2000) -> str:
        """
        질의와 관련된 문서 내용을 프롬프트에 포함할 수 있는 형태로 반환합니다.
        
        Args:
            query: 검색 질의
            max_tokens: 최대 토큰 수
            
        Returns:
            str: 프롬프트에 포함할 컨텍스트 텍스트
        """
        results = self.query(query)
        if not results:
            return ""
        
        context = "다음은 관련 문서에서 추출한 정보입니다:\n\n"
        
        for i, result in enumerate(results, 1):
            content = result["content"].strip()
            source = result["metadata"].get("source", "알 수 없는 출처")
            if isinstance(source, str) and Path(source).exists():
                source = Path(source).name
            
            context += f"[문서 {i}] 출처: {source}\n{content}\n\n"
        
        return context