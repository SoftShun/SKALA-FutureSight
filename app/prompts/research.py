from typing import List, Dict, Any

RESEARCH_SYSTEM_PROMPT = """
당신은 미래 기술 트렌드 분석 프로젝트의 리서치 에이전트입니다.
사용자가 선택한 기술 분야의 향후 5년(2025-2030) 트렌드를 분석하기 위한 정보를 수집합니다.

당신의 임무:
1. 웹 검색을 통해 최신 기술 트렌드 데이터 수집
2. 사용자 제공 문서(RAG)에서 관련 정보 추출
3. 수집된 데이터를 바탕으로 트렌드 분석 실시
4. 다음 예측 논리를 기반으로 트렌드 평가
   - 논문 발행 빈도 및 인용 수
   - 특허 출원 동향
   - 벤처 투자 동향
   - 기술 뉴스 빈도
   - 기업 R&D 투자 동향

객관적이고 논리적인 분석을 제공하세요.
"""

RESEARCH_TASK_PROMPT = """
다음 기술 분야에 대한 미래 트렌드 리서치를 수행해주세요:

기술 분야: {fields}
분석 깊이: {depth}

{rag_context}

다음 정보를 수집 및 분석해주세요:
1. 선택된 기술 분야의 현재 상태 및 배경
2. 향후 5년(2025-2030) 동안의 예상 발전 방향
3. 주요 이해관계자(기업, 연구소, 정부 등)의 동향
4. 분야별 주요 기술 및 혁신 사례
5. 시장 전망 및 상업화 가능성
6. 사회적, 경제적 영향
7. 제약 요소 및 과제

수집한 정보를 체계적으로 정리하여 제공해주세요.
"""

TREND_ANALYSIS_PROMPT = """
수집된 데이터를 바탕으로 다음 기술 분야의 2025-2030년 트렌드를 분석해주세요:

기술 분야: {fields}

다음 기준에 따라 기술의 성장 가능성과 중요도를 평가해주세요:
1. 논문 발행 빈도 및 인용 수: 해당 기술 관련 논문의 발행 빈도와 인용 수 증가 추세
2. 특허 출원 동향: 특허 출원 건수 및 증가율
3. 벤처 투자 동향: 관련 스타트업 및 벤처 투자 규모 및 증가율
4. 기술 뉴스 빈도: 해당 기술 관련 뉴스, 기사 등의 증가 추세
5. 기업 R&D 투자 동향: 주요 기업의 해당 분야 연구개발 투자 규모 및 증가율

각 기준별로 점수(1-10)를 부여하고, 종합 점수를 바탕으로 기술 트렌드를 예측해주세요.
"""

def get_research_system_prompt() -> str:
    """리서치 에이전트의 시스템 프롬프트를 반환합니다."""
    return RESEARCH_SYSTEM_PROMPT

def get_research_task_prompt(
    fields: List[str],
    depth: str,
    rag_enabled: bool = False,
    rag_docs: List[str] = None,
    rag_context: str = None
) -> str:
    """
    리서치 에이전트의 작업 프롬프트를 생성합니다.
    
    Args:
        fields: 선택된 기술 분야 목록
        depth: 분석 깊이
        rag_enabled: RAG 사용 여부
        rag_docs: RAG에 사용되는 문서 목록
        rag_context: RAG 문서에서 추출한 관련 정보
        
    Returns:
        str: 리서치 작업 프롬프트
    """
    fields_str = ", ".join(fields)
    
    rag_info = ""
    if rag_enabled:
        if rag_docs:
            rag_info += f"참조 문서: {', '.join(rag_docs)}\n\n"
        if rag_context:
            rag_info += f"참조 문서 관련 정보:\n{rag_context}\n"
    
    return RESEARCH_TASK_PROMPT.format(
        fields=fields_str,
        depth=depth,
        rag_context=rag_info
    )

def get_trend_analysis_prompt(fields: List[str]) -> str:
    """
    트렌드 분석 프롬프트를 생성합니다.
    
    Args:
        fields: 선택된 기술 분야 목록
        
    Returns:
        str: 트렌드 분석 프롬프트
    """
    fields_str = ", ".join(fields)
    
    return TREND_ANALYSIS_PROMPT.format(fields=fields_str) 