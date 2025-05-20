import os
import json
import time
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path

from app.agents import CoordinatorAgent, ResearchAgent, ReportAgent
from app.tools.converter import ReportConverter

class TrendAnalysisWorkflow:
    """
    기술 트렌드 분석 워크플로우 관리 클래스
    """
    
    def __init__(self):
        """워크플로우 초기화"""
        self.coordinator = CoordinatorAgent()
        self.researcher = ResearchAgent()
        self.reporter = ReportAgent()
        self.converter = ReportConverter()
        
        # 상태 초기화
        self.fields = []
        self.format = "md"
        self.language = "ko"
        self.depth = "standard"
        self.rag_enabled = False
        self.rag_docs = []
        self.output_path = None
    
    def setup(
        self,
        fields: List[str],
        format: str,
        language: str,
        depth: str,
        rag_enabled: bool = False,
        rag_docs: List[str] = None
    ) -> None:
        """
        워크플로우 설정
        
        Args:
            fields: 선택된 기술 분야 목록
            format: 보고서 형식
            language: 보고서 언어
            depth: 분석 깊이
            rag_enabled: RAG 사용 여부
            rag_docs: RAG에 사용되는 문서 목록
        """
        self.fields = fields
        self.format = format
        self.language = language
        self.depth = depth
        self.rag_enabled = rag_enabled
        self.rag_docs = rag_docs or []
        
        # 코디네이터 에이전트 설정
        self.coordinator.set_task_parameters(
            fields=fields,
            format=format,
            language=language,
            depth=depth,
            rag_enabled=rag_enabled,
            rag_docs=self.rag_docs
        )
        
        # 리서치 에이전트 설정
        self.researcher.set_task_parameters(
            fields=fields,
            depth=depth,
            rag_enabled=rag_enabled,
            rag_docs=self.rag_docs
        )
    
    def run(self, callback: Optional[Callable[[str], None]] = None) -> str:
        """
        워크플로우 실행
        
        Args:
            callback: 진행 상황을 보고할 콜백 함수
            
        Returns:
            str: 결과 보고서 파일 경로
        """
        if callback:
            callback("워크플로우 시작")
        
        # 1. 분석 계획 생성
        if callback:
            callback("분석 계획 생성 중...")
        
        analysis_plan = self.coordinator.create_analysis_plan()
        
        # 2. 리서치 수행
        if callback:
            callback("리서치 수행 중...")
        
        research_results = self.researcher.run()
        self.coordinator.process_research_results(research_results)
        
        # 3. 보고서 생성
        if callback:
            callback("보고서 생성 중...")
        
        self.reporter.set_task_parameters(
            fields=self.fields,
            language=self.language,
            depth=self.depth,
            research_data=research_results
        )
        
        report = self.reporter.run()
        self.coordinator.process_report(report)
        
        # 4. 보고서 변환 및 저장
        if callback:
            callback(f"보고서 {self.format} 형식으로 변환 중...")
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"tech_trend_report_{timestamp}"
        
        self.output_path = self.converter.convert(
            markdown_content=report,
            format=self.format,
            filename=filename
        )
        
        if callback:
            callback(f"워크플로우 완료: {self.output_path}")
        
        return self.output_path 