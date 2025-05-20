import os
import sys
import typer
from typing import Optional, List
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from app.interface.cli import get_user_input

# 기존 워크플로우 대신 새로운 LangGraph 기반 워크플로우 사용
from app.workflow_graph import TrendAnalysisGraphWorkflow

# 환경 변수 로드
load_dotenv()

# 콘솔 초기화
console = Console()

# 앱 초기화
app = typer.Typer()

@app.command()
def run():
    """미래 기술 트렌드 분석 도구 실행"""
    # OpenAI API 키 확인
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[bold red]오류: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.[/bold red]")
        console.print("OpenAI API 키를 .env 파일에 설정하거나 환경 변수로 설정해주세요.")
        return
    
    try:
        # 사용자 입력 수집
        user_input = get_user_input()
        
        # LangGraph 기반 워크플로우 초기화 및 설정
        workflow = TrendAnalysisGraphWorkflow()
        workflow.setup(
            fields=user_input["selected_fields"],
            format=user_input["report_format"],
            language=user_input["language"],
            depth=user_input["analysis_depth"],
            rag_enabled=user_input["use_rag"],
            rag_docs=user_input["rag_documents"]
        )
        
        # 프로그레스 바 설정
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("", total=None)
            
            # 콜백 함수 정의
            def update_progress(message: str):
                progress.update(task, description=message)
            
            # 워크플로우 실행
            output_path = workflow.run(callback=update_progress)
        
        # 결과 출력
        console.print(f"\n[bold green]보고서가 생성되었습니다: {output_path}[/bold green]")
    
    except Exception as e:
        console.print(f"[bold red]오류가 발생했습니다: {str(e)}[/bold red]")
        import traceback
        console.print(traceback.format_exc())
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(app()) 