import os
import json
from typing import Dict, List, Any, Optional

from app.agents.base import BaseAgent
from app.prompts.research import (
    get_research_system_prompt,
    get_research_task_prompt,
    get_trend_analysis_prompt
)
from app.tools.search import WebSearchTool
from app.tools.rag import RAGSystem

class ResearchAgent(BaseAgent):
    """
    리서치 에이전트 클래스
    웹 검색과 RAG 시스템을 활용하여 기술 분야 정보를 수집하고 분석합니다.
    """
    
    def __init__(
        self,
        model: str = "gpt-4o",
        temperature: float = 0.4,
        max_tokens: int = 4000
    ):
        """
        ResearchAgent 초기화
        
        Args:
            model: 사용할 모델명
            temperature: 모델 temperature
            max_tokens: 최대 토큰 수
        """
        system_prompt = get_research_system_prompt()
        super().__init__(
            system_prompt=system_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # 검색 도구 초기화
        self.search_tool = WebSearchTool()
        
        # RAG 시스템 초기화 (문서는 나중에 설정)
        self.rag_system = None
        
        # 리서치 상태 초기화
        self.update_state("fields", [])
        self.update_state("depth", "standard")
        self.update_state("rag_enabled", False)
        self.update_state("rag_docs", [])
        self.update_state("search_results", {})
        self.update_state("rag_results", {})
        self.update_state("analysis_results", None)
    
    def set_task_parameters(
        self,
        fields: List[str],
        depth: str,
        rag_enabled: bool = False,
        rag_docs: List[str] = None
    ) -> None:
        """
        작업 파라미터 설정
        
        Args:
            fields: 선택된 기술 분야 목록
            depth: 분석 깊이
            rag_enabled: RAG 사용 여부
            rag_docs: RAG에 사용되는 문서 목록
        """
        self.update_state("fields", fields)
        self.update_state("depth", depth)
        self.update_state("rag_enabled", rag_enabled)
        self.update_state("rag_docs", rag_docs or [])
        
        # RAG 시스템 초기화 (문서가 있는 경우)
        if rag_enabled and rag_docs:
            self.rag_system = RAGSystem(documents=rag_docs)
    
    def search_field_information(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        기술 분야 정보 검색 - analyze_trends 함수 사용
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: 기술 분야별 검색 결과
        """
        search_results = {}
        fields = self.get_state("fields")
        
        for field in fields:
            # analyze_trends 함수를 사용하여 여러 측면에서 데이터 수집
            trend_analysis = self.search_tool.analyze_trends(field)
            
            # 각 측면의 결과를 하나의 리스트로 통합
            field_results = []
            for aspect, results in trend_analysis.items():
                # 각 측면별 결과에서 count를 5로 수정
                for aspect_result in results:
                    field_results.append(aspect_result)
            
            search_results[field] = field_results
        
        self.update_state("search_results", search_results)
        return search_results
    
    def query_rag_system(self) -> Dict[str, List[str]]:
        """
        RAG 시스템 쿼리
        
        Returns:
            Dict[str, List[str]]: 기술 분야별 RAG 결과
        """
        if not self.get_state("rag_enabled") or not self.rag_system:
            return {}
        
        rag_results = {}
        fields = self.get_state("fields")
        
        for field in fields:
            # 기본 RAG 쿼리
            queries = [
                f"{field} 기술의 현재 상태와 향후 발전 방향은?",
                f"{field} 분야의 주요 기술 혁신과 개발 동향은?",
                f"{field} 시장 전망과 주요 기업들의 동향은?",
                f"{field} 기술이 사회와 경제에 미치는 영향은?"
            ]
            
            field_results = []
            for query in queries:
                results = self.rag_system.query(query)
                if results:
                    field_results.append(results)
            
            rag_results[field] = field_results
        
        self.update_state("rag_results", rag_results)
        return rag_results
    
    def analyze_trends(self) -> str:
        """
        트렌드 분석 수행
        
        Returns:
            str: 트렌드 분석 결과
        """
        fields = self.get_state("fields")
        search_results = self.get_state("search_results")
        rag_results = self.get_state("rag_results")
        
        # 검색 결과 요약
        search_summary = ""
        for field, results in search_results.items():
            search_summary += f"\n## {field} 검색 결과 요약\n\n"
            for i, result in enumerate(results[:5]):  # 상위 5개 결과만 사용
                search_summary += f"- {result.get('title', '제목 없음')}: {result.get('snippet', '내용 없음')[:200]}...\n"
        
        # RAG 결과 요약
        rag_summary = ""
        if self.get_state("rag_enabled"):
            for field, results in rag_results.items():
                rag_summary += f"\n## {field} RAG 결과 요약\n\n"
                for i, result in enumerate(results[:3]):  # 상위 3개 결과만 사용
                    rag_summary += f"- 쿼리 {i+1} 결과: {result[:300]}...\n"
        
        # 트렌드 분석 프롬프트 생성
        trend_prompt = get_trend_analysis_prompt(fields)
        
        # 검색 및 RAG 결과 추가
        input_text = f"{trend_prompt}\n\n검색 결과:\n{search_summary}\n\nRAG 결과:\n{rag_summary}"
        
        # 분석 결과 생성
        response = self.llm.invoke(input_text)
        analysis = response.content
        
        self.update_state("analysis_results", analysis)
        return analysis
    
    def get_task_prompt(self) -> str:
        """
        작업 프롬프트 생성
        
        Returns:
            str: 작업 프롬프트
        """
        # RAG 문서에서 추출한 관련 정보
        rag_context = None
        if self.get_state("rag_enabled") and self.get_state("rag_results"):
            rag_context = json.dumps(self.get_state("rag_results"), indent=2)
        
        return get_research_task_prompt(
            fields=self.get_state("fields"),
            depth=self.get_state("depth"),
            rag_enabled=self.get_state("rag_enabled"),
            rag_docs=self.get_state("rag_docs"),
            rag_context=rag_context
        )
    
    def run(self, input_text: str = None, **kwargs) -> str:
        """
        리서치 에이전트 실행
        
        Args:
            input_text: 입력 텍스트 (없으면 기본 작업 프롬프트 사용)
            **kwargs: 추가 인자
            
        Returns:
            str: 리서치 결과
        """
        # 웹 검색 수행
        search_results = self.search_field_information()
        
        # RAG 시스템 쿼리 (RAG가 활성화된 경우)
        if self.get_state("rag_enabled"):
            rag_results = self.query_rag_system()
        
        # 트렌드 분석 수행
        analysis = self.analyze_trends()
        
        if input_text is None:
            input_text = self.get_task_prompt()
        
        # 검색 결과와 분석 결과를 입력에 추가
        search_summary = json.dumps(search_results, indent=2)
        enriched_input = f"{input_text}\n\n검색 결과:\n{search_summary}\n\n분석 결과:\n{analysis}"
        
        # 최종 리서치 보고서 생성
        response = self.llm.invoke(enriched_input)
        
        # 히스토리에 기록
        self.add_to_history("user", enriched_input)
        self.add_to_history("assistant", response.content)
        
        return response.content 