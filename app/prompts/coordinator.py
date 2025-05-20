from typing import List, Dict, Any

COORDINATOR_SYSTEM_PROMPT = """
당신은 미래 기술 트렌드 분석 프로젝트의 코디네이터 에이전트입니다.
사용자가 선택한 기술 분야의 향후 5년(2025-2030) 트렌드를 분석하는 전체 과정을 조율합니다.

당신의 임무:
1. 사용자 입력을 받아 분석 계획을 수립합니다.
2. 리서치 에이전트에게 웹 검색과 RAG 데이터 분석 작업을 지시합니다.
3. 리서치 결과를 종합하여 리포트 에이전트에게 보고서 작성을 지시합니다.
4. 사용자가 선택한 형식과 언어로 최종 보고서를 생성합니다.

항상 명확하고 전문적인 태도를 유지하세요.
"""

COORDINATOR_TASK_PROMPT = """
다음 기술 분야의 미래 트렌드 분석 보고서 생성 작업을 조율해주세요.

선택된 기술 분야: {fields}
보고서 형식: {format}
보고서 언어: {language}
분석 깊이: {depth}

{rag_context}

분석 계획을 수립하고, 적절한 에이전트에게 작업을 할당해주세요.
"""

COORDINATOR_REPORT_PLANNING_PROMPT = """
다음 정보를 바탕으로 기술 트렌드 분석 보고서의 개요를 작성해주세요:

기술 분야: {fields}
보고서 언어: {language}
분석 깊이: {depth}

다음 정보가 보고서에 포함되어야 합니다:
1. 선택된 기술 분야의 현재 상태 및 배경
2. 향후 5년(2025-2030) 동안의 예상 발전 방향
3. 주요 이해관계자(기업, 연구소, 정부 등)의 동향
4. 분야별 주요 기술 및 혁신 사례
5. 시장 전망 및 상업화 가능성
6. 사회적, 경제적 영향
7. 제약 요소 및 과제
8. 결론 및 제언

보고서는 전문적이고 논리적인 구조를 가져야 하며, 객관적인 데이터와 분석을 바탕으로 해야 합니다.
"""

def get_coordinator_system_prompt() -> str:
    """코디네이터 에이전트의 시스템 프롬프트를 반환합니다."""
    return COORDINATOR_SYSTEM_PROMPT

def get_coordinator_task_prompt(
    fields: List[str],
    format: str,
    language: str,
    depth: str,
    rag_enabled: bool = False,
    rag_docs: List[str] = None
) -> str:
    """
    코디네이터 에이전트의 작업 프롬프트를 생성합니다.
    
    Args:
        fields: 선택된 기술 분야 목록
        format: 보고서 형식
        language: 보고서 언어
        depth: 분석 깊이
        rag_enabled: RAG 사용 여부
        rag_docs: RAG에 사용되는 문서 목록
        
    Returns:
        str: 코디네이터 작업 프롬프트
    """
    fields_str = ", ".join(fields)
    
    rag_context = ""
    if rag_enabled and rag_docs:
        rag_context = f"RAG 참조 문서: {', '.join(rag_docs)}"
    
    return COORDINATOR_TASK_PROMPT.format(
        fields=fields_str,
        format=format,
        language=language,
        depth=depth,
        rag_context=rag_context
    )

def get_report_planning_prompt(
    fields: List[str],
    language: str,
    depth: str
) -> str:
    """
    보고서 계획 프롬프트를 생성합니다.
    
    Args:
        fields: 선택된 기술 분야 목록
        language: 보고서 언어
        depth: 분석 깊이
        
    Returns:
        str: 보고서 계획 프롬프트
    """
    fields_str = ", ".join(fields)
    
    return COORDINATOR_REPORT_PLANNING_PROMPT.format(
        fields=fields_str,
        language=language,
        depth=depth
    ) 