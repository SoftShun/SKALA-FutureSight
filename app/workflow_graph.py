import os
import json
import time
from typing import Dict, List, Any, Optional, TypedDict, Annotated, Callable
from pathlib import Path

from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from app.agents import CoordinatorAgent, ResearchAgent, ReportAgent
from app.tools.converter import ReportConverter

# 상태 유형 정의
class TrendAnalysisState(TypedDict):
    """기술 트렌드 분석 워크플로우의 상태를 정의합니다."""
    fields: List[str]
    format: str
    language: str
    depth: str
    rag_enabled: bool
    rag_docs: List[str]
    analysis_plan: Optional[Dict[str, Any]]
    research_results: Optional[str]
    report: Optional[str]
    output_path: Optional[str]
    status: str
    error: Optional[str]
    callback: Optional[Callable[[str], None]]

# 노드 함수 정의
def create_analysis_plan(state: TrendAnalysisState) -> TrendAnalysisState:
    """분석 계획을 생성합니다."""
    # 상태 업데이트
    if state.get("callback"):
        state["callback"]("분석 계획 생성 중...")
    
    try:
        # 코디네이터 에이전트 초기화
        coordinator = CoordinatorAgent()
        
        # 코디네이터 설정
        coordinator.set_task_parameters(
            fields=state["fields"],
            format=state["format"],
            language=state["language"],
            depth=state["depth"],
            rag_enabled=state["rag_enabled"],
            rag_docs=state["rag_docs"]
        )
        
        # 분석 계획 생성
        analysis_plan = coordinator.create_analysis_plan()
        
        # 상태 업데이트
        state["analysis_plan"] = analysis_plan
        state["status"] = "analysis_plan_created"
        state["error"] = None
        
        return state
    except Exception as e:
        state["error"] = f"분석 계획 생성 중 오류 발생: {str(e)}"
        state["status"] = "error"
        return state

def perform_research(state: TrendAnalysisState) -> TrendAnalysisState:
    """리서치를 수행합니다."""
    # 상태 업데이트
    if state.get("callback"):
        state["callback"]("리서치 수행 중...")
    
    try:
        # 리서치 에이전트 초기화
        researcher = ResearchAgent()
        
        # 리서치 에이전트 설정
        researcher.set_task_parameters(
            fields=state["fields"],
            depth=state["depth"],
            rag_enabled=state["rag_enabled"],
            rag_docs=state["rag_docs"]
        )
        
        # 리서치 수행
        research_results = researcher.run()
        
        # 상태 업데이트
        state["research_results"] = research_results
        state["status"] = "research_completed"
        state["error"] = None
        
        return state
    except Exception as e:
        state["error"] = f"리서치 수행 중 오류 발생: {str(e)}"
        state["status"] = "error"
        return state

def generate_report(state: TrendAnalysisState) -> TrendAnalysisState:
    """보고서를 생성합니다."""
    # 상태 업데이트
    if state.get("callback"):
        state["callback"]("보고서 생성 중...")
    
    try:
        # 리포트 에이전트 초기화
        reporter = ReportAgent()
        
        # 리포트 에이전트 설정
        reporter.set_task_parameters(
            fields=state["fields"],
            language=state["language"],
            depth=state["depth"],
            research_data=state["research_results"]
        )
        
        # 보고서 생성
        report = reporter.run()
        
        # 상태 업데이트
        state["report"] = report
        state["status"] = "report_generated"
        state["error"] = None
        
        return state
    except Exception as e:
        state["error"] = f"보고서 생성 중 오류 발생: {str(e)}"
        state["status"] = "error"
        return state

def convert_report(state: TrendAnalysisState) -> TrendAnalysisState:
    """보고서를 변환합니다."""
    # 상태 업데이트
    if state.get("callback"):
        state["callback"](f"보고서 {state['format']} 형식으로 변환 중...")
    
    try:
        # 보고서 변환기 초기화
        converter = ReportConverter()
        
        # 타임스탬프 생성
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"tech_trend_report_{timestamp}"
        
        # 보고서 변환
        output_path = converter.convert(
            markdown_content=state["report"],
            format=state["format"],
            filename=filename
        )
        
        # 상태 업데이트
        state["output_path"] = output_path
        state["status"] = "completed"
        state["error"] = None
        
        if state.get("callback"):
            state["callback"](f"워크플로우 완료: {output_path}")
        
        return state
    except Exception as e:
        state["error"] = f"보고서 변환 중 오류 발생: {str(e)}"
        state["status"] = "error"
        return state

def handle_error(state: TrendAnalysisState) -> TrendAnalysisState:
    """오류를 처리합니다."""
    if state.get("callback"):
        state["callback"](f"오류 발생: {state.get('error', '알 수 없는 오류')}")
    
    # 여기서 추가적인 오류 처리 로직을 구현할 수 있습니다.
    # 예: 로깅, 알림 등
    
    return state

# 조건부 라우팅 함수
def should_handle_error(state: TrendAnalysisState) -> str:
    """상태에 오류가 있는지 확인하고 라우팅합니다."""
    if state.get("error"):
        return "error"
    return "continue"

class TrendAnalysisGraphWorkflow:
    """LangGraph를 사용한 기술 트렌드 분석 워크플로우 클래스"""
    
    def __init__(self):
        """워크플로우 초기화"""
        # 그래프 빌드
        builder = StateGraph(TrendAnalysisState)
        
        # 노드 추가
        builder.add_node("create_plan", create_analysis_plan)
        builder.add_node("perform_research", perform_research)
        builder.add_node("generate_report", generate_report)
        builder.add_node("convert_report", convert_report)
        builder.add_node("handle_error", handle_error)
        
        # START 노드에서 첫 번째 노드로의 에지 추가 (중요!)
        builder.add_edge("START", "create_plan")
        
        # 에지 추가 (기본 흐름)
        builder.add_edge("create_plan", "perform_research")
        builder.add_edge("perform_research", "generate_report")
        builder.add_edge("generate_report", "convert_report")
        
        # 조건부 에지 추가 (오류 처리)
        builder.add_conditional_edges(
            "create_plan",
            should_handle_error,
            {
                "error": "handle_error",
                "continue": "perform_research"
            }
        )
        
        builder.add_conditional_edges(
            "perform_research",
            should_handle_error,
            {
                "error": "handle_error",
                "continue": "generate_report"
            }
        )
        
        builder.add_conditional_edges(
            "generate_report",
            should_handle_error,
            {
                "error": "handle_error",
                "continue": "convert_report"
            }
        )
        
        builder.add_conditional_edges(
            "convert_report",
            should_handle_error,
            {
                "error": "handle_error",
                "continue": "END"
            }
        )
        
        # 오류 처리 노드는 종료로 설정
        builder.add_edge("handle_error", "END")
        
        # 그래프 컴파일
        self.graph = builder.compile()
        
        # 체크포인트 설정
        self.memory_saver = MemorySaver()
        
        # 상태 초기화
        self.fields = []
        self.format = "md"
        self.language = "ko"
        self.depth = "standard"
        self.rag_enabled = False
        self.rag_docs = []
        self.output_path = None
        self.callback = None
    
    def setup(
        self,
        fields: List[str],
        format: str,
        language: str,
        depth: str,
        rag_enabled: bool = False,
        rag_docs: List[str] = None,
        callback: Optional[Callable[[str], None]] = None
    ) -> None:
        """워크플로우 설정"""
        self.fields = fields
        self.format = format
        self.language = language
        self.depth = depth
        self.rag_enabled = rag_enabled
        self.rag_docs = rag_docs or []
        self.callback = callback
    
    def run(self, callback: Optional[Callable[[str], None]] = None) -> str:
        """워크플로우 실행"""
        # 콜백 업데이트 (설정에서 호출된 경우)
        if callback:
            self.callback = callback
            
        # 초기 상태 설정
        initial_state = TrendAnalysisState(
            fields=self.fields,
            format=self.format,
            language=self.language,
            depth=self.depth,
            rag_enabled=self.rag_enabled,
            rag_docs=self.rag_docs,
            analysis_plan=None,
            research_results=None,
            report=None,
            output_path=None,
            status="starting",
            error=None,
            callback=self.callback
        )
        
        # 콜백 호출
        if self.callback:
            self.callback("워크플로우 시작")
        
        # 그래프 실행
        config = {"recursion_limit": 25}
        result = self.graph.run(
            initial_state,
            config,
            checkpoint_saver=self.memory_saver
        )
        
        # 결과 반환
        if result.get("error"):
            raise RuntimeError(result["error"])
        
        return result.get("output_path", "")