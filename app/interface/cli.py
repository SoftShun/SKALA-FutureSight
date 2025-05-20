import os
import typer
from typing import Dict, List, Tuple, Optional, Any
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

console = Console()

# 기술 분야 정의
TECH_FIELDS = {
    "ai": "인공지능(AI)",
    "robotics": "로보틱스",
    "energy": "에너지 기술",
    "biotech": "생명과학/바이오테크"
}

# 보고서 형식 정의
REPORT_FORMATS = {
    "md": "Markdown",
    "pdf": "PDF",
    "docx": "Word(DOCX)"
}

# 보고서 언어 정의
REPORT_LANGUAGES = {
    "ko": "한국어",
    "en": "영어"
}

# 분석 깊이 정의
ANALYSIS_DEPTH = {
    "standard": "표준 분석",
    "deep": "심층 분석"
}

def display_welcome():
    """시작 메시지를 표시합니다."""
    console.print("\n[bold blue]미래 기술 트렌드 분석 도구[/bold blue]")
    console.print("선택한 기술 분야의 향후 5년(2025-2030) 트렌드를 분석합니다.\n")

def select_fields() -> List[str]:
    """사용자가 분석할 기술 분야를 선택합니다 (1-3개)."""
    console.print("\n[bold]분석할 기술 분야를 선택하세요 (1-3개):[/bold]")
    
    for key, value in TECH_FIELDS.items():
        console.print(f"  [cyan]{key}[/cyan]: {value}")
    
    selected = []
    while not selected:
        fields_input = Prompt.ask("선택할 분야 (쉼표로 구분, 예: ai,robotics)")
        fields = [f.strip().lower() for f in fields_input.split(",")]
        
        # 유효성 검사
        invalid_fields = [f for f in fields if f not in TECH_FIELDS]
        if invalid_fields:
            console.print(f"[bold red]오류: 잘못된 분야 - {', '.join(invalid_fields)}[/bold red]")
            continue
        
        if len(fields) < 1 or len(fields) > 3:
            console.print("[bold red]오류: 1-3개의 분야를 선택해야 합니다.[/bold red]")
            continue
        
        selected = fields
    
    console.print("\n[bold green]선택된 분야:[/bold green]")
    for field in selected:
        console.print(f"  - {TECH_FIELDS[field]}")
    
    return selected

def select_report_format() -> str:
    """보고서 형식을 선택합니다."""
    console.print("\n[bold]출력 보고서 형식을 선택하세요:[/bold]")
    
    for key, value in REPORT_FORMATS.items():
        console.print(f"  [cyan]{key}[/cyan]: {value}")
    
    while True:
        format_input = Prompt.ask("선택할 형식", choices=list(REPORT_FORMATS.keys()), default="md")
        if format_input in REPORT_FORMATS:
            return format_input

def select_language() -> str:
    """보고서 언어를 선택합니다."""
    console.print("\n[bold]보고서 언어를 선택하세요:[/bold]")
    
    for key, value in REPORT_LANGUAGES.items():
        console.print(f"  [cyan]{key}[/cyan]: {value}")
    
    while True:
        lang_input = Prompt.ask("선택할 언어", choices=list(REPORT_LANGUAGES.keys()), default="ko")
        if lang_input in REPORT_LANGUAGES:
            return lang_input

def select_depth() -> str:
    """분석 깊이를 선택합니다."""
    console.print("\n[bold]분석 깊이를 선택하세요:[/bold]")
    
    for key, value in ANALYSIS_DEPTH.items():
        console.print(f"  [cyan]{key}[/cyan]: {value}")
    
    while True:
        depth_input = Prompt.ask("선택할 분석 깊이", choices=list(ANALYSIS_DEPTH.keys()), default="standard")
        if depth_input in ANALYSIS_DEPTH:
            return depth_input

def manage_rag_documents() -> Dict[str, Any]:
    """RAG 문서를 관리합니다."""
    from app.data.processor import DocumentManager
    
    doc_manager = DocumentManager()
    registered_docs = doc_manager.list_documents()
    
    # 등록된 문서 표시
    if registered_docs:
        console.print("\n[bold]등록된 RAG 문서:[/bold]")
        for i, doc in enumerate(registered_docs, 1):
            console.print(f"  {i}. {doc}")
    else:
        console.print("\n[bold yellow]등록된 RAG 문서가 없습니다.[/bold yellow]")
    
    # 문서 관리 메뉴
    console.print("\n[bold]RAG 문서 관리:[/bold]")
    console.print("  [cyan]1[/cyan]: 문서 추가")
    console.print("  [cyan]2[/cyan]: 문서 삭제")
    console.print("  [cyan]3[/cyan]: 계속 진행")
    
    action = Prompt.ask("선택", choices=["1", "2", "3"], default="3")
    
    if action == "1":
        # 문서 추가
        if len(registered_docs) >= 2:
            console.print("[bold red]최대 2개의 문서만 등록할 수 있습니다.[/bold red]")
            return manage_rag_documents()
        
        console.print("\n[bold]추가할 문서 경로를 입력하세요 (PDF, DOCX, TXT, MD 파일 지원):[/bold]")
        doc_path = Prompt.ask("문서 경로")
        
        if not os.path.exists(doc_path):
            console.print(f"[bold red]오류: 파일을 찾을 수 없습니다 - {doc_path}[/bold red]")
            return manage_rag_documents()
        
        try:
            doc_manager.add_document(doc_path)
            console.print(f"[bold green]문서가 추가되었습니다: {doc_path}[/bold green]")
        except Exception as e:
            console.print(f"[bold red]문서 추가 중 오류 발생: {str(e)}[/bold red]")
        
        return manage_rag_documents()
    
    elif action == "2":
        # 문서 삭제
        if not registered_docs:
            console.print("[bold yellow]삭제할 문서가 없습니다.[/bold yellow]")
            return manage_rag_documents()
        
        console.print("\n[bold]삭제할 문서 번호를 선택하세요:[/bold]")
        doc_idx = int(Prompt.ask("문서 번호", choices=[str(i) for i in range(1, len(registered_docs) + 1)]))
        
        try:
            doc_manager.delete_document(registered_docs[doc_idx - 1])
            console.print(f"[bold green]문서가 삭제되었습니다: {registered_docs[doc_idx - 1]}[/bold green]")
        except Exception as e:
            console.print(f"[bold red]문서 삭제 중 오류 발생: {str(e)}[/bold red]")
        
        return manage_rag_documents()
    
    # 현재 등록된 문서 정보 반환
    return {
        "rag_documents": doc_manager.list_documents(),
        "use_rag": len(doc_manager.list_documents()) > 0
    }

def get_user_input() -> Dict[str, Any]:
    """사용자 입력을 수집합니다."""
    display_welcome()
    
    # RAG 문서 관리
    rag_info = manage_rag_documents()
    
    # 기술 분야 선택
    selected_fields = select_fields()
    
    # 보고서 형식 선택
    report_format = select_report_format()
    
    # 보고서 언어 선택
    language = select_language()
    
    # 분석 깊이 선택
    depth = select_depth()
    
    # RAG 사용 여부 확인 (등록된 문서가 있는 경우)
    use_rag = False
    if rag_info["rag_documents"]:
        use_rag = Confirm.ask("\nRAG 기능을 사용하시겠습니까? (등록된 문서를 분석에 활용)")
    
    # 최종 확인
    console.print("\n[bold]분석 설정 요약:[/bold]")
    console.print(f"  분석 분야: {', '.join([TECH_FIELDS[f] for f in selected_fields])}")
    console.print(f"  보고서 형식: {REPORT_FORMATS[report_format]}")
    console.print(f"  보고서 언어: {REPORT_LANGUAGES[language]}")
    console.print(f"  분석 깊이: {ANALYSIS_DEPTH[depth]}")
    console.print(f"  RAG 사용: {'예' if use_rag else '아니오'}")
    
    if not Confirm.ask("\n분석을 시작하시겠습니까?"):
        raise typer.Abort()
    
    return {
        "selected_fields": selected_fields,
        "report_format": report_format,
        "language": language,
        "analysis_depth": depth,
        "rag_documents": rag_info["rag_documents"] if use_rag else [],
        "use_rag": use_rag
    } 