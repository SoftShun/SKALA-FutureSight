import os
import json
from typing import Dict, List, Any, Optional

from app.agents.base import BaseAgent
from app.prompts.coordinator import (
    get_coordinator_system_prompt,
    get_coordinator_task_prompt,
    get_report_planning_prompt
)

class CoordinatorAgent(BaseAgent):
    """
    코디네이터 에이전트 클래스
    전체 분석 프로세스를 조율합니다.
    """
    
    def __init__(
        self,
        model: str = "gpt-4o",
        temperature: float = 0.3,
        max_tokens: int = 4000
    ):
        """
        CoordinatorAgent 초기화
        
        Args:
            model: 사용할 모델명
            temperature: 모델 temperature
            max_tokens: 최대 토큰 수
        """
        system_prompt = get_coordinator_system_prompt()
        super().__init__(
            system_prompt=system_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # 코디네이터 상태 초기화
        self.update_state("fields", [])
        self.update_state("format", "md")
        self.update_state("language", "ko")
        self.update_state("depth", "standard")
        self.update_state("rag_enabled", False)
        self.update_state("rag_docs", [])
        self.update_state("plan", None)
        self.update_state("research_results", None)
        self.update_state("report", None)
    
    def set_task_parameters(
        self,
        fields: List[str],
        format: str,
        language: str,
        depth: str,
        rag_enabled: bool = False,
        rag_docs: List[str] = None
    ) -> None:
        """
        작업 파라미터 설정
        
        Args:
            fields: 선택된 기술 분야 목록
            format: 보고서 형식
            language: 보고서 언어
            depth: 분석 깊이
            rag_enabled: RAG 사용 여부
            rag_docs: RAG에 사용되는 문서 목록
        """
        self.update_state("fields", fields)
        self.update_state("format", format)
        self.update_state("language", language)
        self.update_state("depth", depth)
        self.update_state("rag_enabled", rag_enabled)
        self.update_state("rag_docs", rag_docs or [])
    
    def create_analysis_plan(self) -> Dict[str, Any]:
        """
        분석 계획 생성
        
        Returns:
            Dict[str, Any]: 분석 계획
        """
        fields = self.get_state("fields")
        language = self.get_state("language")
        depth = self.get_state("depth")
        
        prompt = get_report_planning_prompt(
            fields=fields,
            language=language,
            depth=depth
        )
        
        response = self.llm.invoke(prompt)
        plan = response.content
        
        self.update_state("plan", plan)
        
        return {
            "fields": fields,
            "language": language,
            "depth": depth,
            "plan": plan
        }
    
    def process_research_results(self, research_results: str) -> None:
        """
        리서치 결과 처리
        
        Args:
            research_results: 리서치 에이전트의 결과
        """
        self.update_state("research_results", research_results)
    
    def process_report(self, report: str) -> None:
        """
        보고서 처리
        
        Args:
            report: 리포트 에이전트의 결과
        """
        self.update_state("report", report)
    
    def get_task_prompt(self) -> str:
        """
        작업 프롬프트 생성
        
        Returns:
            str: 작업 프롬프트
        """
        return get_coordinator_task_prompt(
            fields=self.get_state("fields"),
            format=self.get_state("format"),
            language=self.get_state("language"),
            depth=self.get_state("depth"),
            rag_enabled=self.get_state("rag_enabled"),
            rag_docs=self.get_state("rag_docs")
        )
    
    def run(self, input_text: str = None, **kwargs) -> str:
        """
        코디네이터 에이전트 실행
        
        Args:
            input_text: 입력 텍스트 (없으면 기본 작업 프롬프트 사용)
            **kwargs: 추가 인자
            
        Returns:
            str: 코디네이터 응답
        """
        if input_text is None:
            input_text = self.get_task_prompt()
        
        # 응답 생성
        response = self.llm.invoke(input_text)
        
        # 히스토리에 기록
        self.add_to_history("user", input_text)
        self.add_to_history("assistant", response.content)
        
        return response.content 