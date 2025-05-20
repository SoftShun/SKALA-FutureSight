from typing import List, Dict, Any

REPORT_SYSTEM_PROMPT = """
당신은 미래 기술 트렌드 분석 프로젝트의 리포트 에이전트입니다.
리서치 데이터를 바탕으로 전문적이고 통찰력 있는 기술 트렌드 보고서를 작성합니다.

당신의 임무:
1. 리서치 데이터를 종합하여 논리적이고 일관된 보고서 작성
2. 정성적, 정량적 분석을 모두 포함한 균형 잡힌 내용 제공
3. 사용자가 선택한 언어로 보고서 작성 (한국어/영어)
4. 보고서를 마크다운 형식으로 작성하여 변환 도구로 전달

전문적이고 명확한 언어를 사용하세요. 객관적 사실과 데이터를 바탕으로 한 논리적 분석을 제공하세요.
"""

REPORT_TASK_PROMPT = """
다음 정보를 바탕으로 미래 기술 트렌드 분석 보고서를 작성해주세요:

기술 분야: {fields}
보고서 언어: {language}
분석 깊이: {depth}

리서치 데이터:
{research_data}

보고서는 다음 구조를 따라야 합니다:
1. 제목 및 개요
2. 서론
   - 분석 배경 및 목적
   - 방법론 설명
3. 현재 기술 동향
   - 기술 분야별 현황
   - 주요 기술 개발 현황
   - 핵심 이해관계자 분석
4. 미래 트렌드 예측 (2025-2030)
   - 기술 발전 방향
   - 예상 혁신 사례
   - 주요 기술별 성장 가능성 평가
5. 시장 전망
   - 시장 규모 및 성장률 예측
   - 상업화 가능성 및 시장 진입 시점
   - 주요 기업 및 경쟁 구도
6. 사회경제적 영향
   - 산업 구조 변화
   - 일자리 및 직무 변화
   - 규제 및 정책 방향
7. 제약 요소 및 과제
   - 기술적 장벽
   - 윤리적, 법적 문제
   - 사회적 수용성
8. 결론 및 제언
9. 참고 문헌

마크다운 형식으로 작성해주세요. 표, 목록 등을 적절히 활용하여 가독성을 높여주세요.
"""

def get_report_system_prompt() -> str:
    """리포트 에이전트의 시스템 프롬프트를 반환합니다."""
    return REPORT_SYSTEM_PROMPT

def get_report_task_prompt(
    fields: List[str],
    language: str,
    depth: str,
    research_data: str
) -> str:
    """
    리포트 에이전트의 작업 프롬프트를 생성합니다.
    
    Args:
        fields: 선택된 기술 분야 목록
        language: 보고서 언어
        depth: 분석 깊이
        research_data: 리서치 데이터
        
    Returns:
        str: 리포트 작업 프롬프트
    """
    fields_str = ", ".join(fields)
    
    return REPORT_TASK_PROMPT.format(
        fields=fields_str,
        language=language,
        depth=depth,
        research_data=research_data
    ) 