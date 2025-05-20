import os
import json
from typing import Dict, List, Any, Optional

from app.agents.base import BaseAgent
from app.prompts.report import (
    get_report_system_prompt,
    get_report_task_prompt
)

class ReportAgent(BaseAgent):
    """
    리포트 에이전트 클래스
    리서치 데이터를 바탕으로 기술 트렌드 보고서를 작성합니다.
    """
    
    def __init__(
        self,
        model: str = "gpt-4o",
        temperature: float = 0.5,
        max_tokens: int = 4000
    ):
        """
        ReportAgent 초기화
        
        Args:
            model: 사용할 모델명
            temperature: 모델 temperature
            max_tokens: 최대 토큰 수
        """
        system_prompt = get_report_system_prompt()
        super().__init__(
            system_prompt=system_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # 리포트 상태 초기화
        self.update_state("fields", [])
        self.update_state("language", "ko")
        self.update_state("depth", "standard")
        self.update_state("research_data", None)
        self.update_state("report", None)
    
    def set_task_parameters(
        self,
        fields: List[str],
        language: str,
        depth: str,
        research_data: str
    ) -> None:
        """
        작업 파라미터 설정
        
        Args:
            fields: 선택된 기술 분야 목록
            language: 보고서 언어
            depth: 분석 깊이
            research_data: 리서치 데이터
        """
        self.update_state("fields", fields)
        self.update_state("language", language)
        self.update_state("depth", depth)
        self.update_state("research_data", research_data)
    
    def get_task_prompt(self) -> str:
        """
        작업 프롬프트 생성
        
        Returns:
            str: 작업 프롬프트
        """
        return get_report_task_prompt(
            fields=self.get_state("fields"),
            language=self.get_state("language"),
            depth=self.get_state("depth"),
            research_data=self.get_state("research_data")
        )
    
    def generate_report(self) -> str:
        """
        보고서 생성
        
        Returns:
            str: 생성된 보고서
        """
        prompt = self.get_task_prompt()
        
        # 보고서 생성
        response = self.llm.invoke(prompt)
        report = response.content
        
        self.update_state("report", report)
        
        return report
    
    def run(self, input_text: str = None, **kwargs) -> str:
        """
        리포트 에이전트 실행
        
        Args:
            input_text: 입력 텍스트 (없으면 기본 작업 프롬프트 사용)
            **kwargs: 추가 인자
            
        Returns:
            str: 생성된 보고서
        """
        if input_text is None:
            input_text = self.get_task_prompt()
        
        # 보고서 생성
        response = self.llm.invoke(input_text)
        report = response.content
        
        # 히스토리에 기록
        self.add_to_history("user", input_text)
        self.add_to_history("assistant", report)
        
        self.update_state("report", report)
        
        return report 