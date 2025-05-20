import os
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class BaseAgent(ABC):
    """
    에이전트 기본 클래스
    모든 에이전트는 이 클래스를 상속받아 구현합니다.
    """
    
    def __init__(
        self,
        system_prompt: str,
        model: str = "gpt-4o",
        temperature: float = 0.3,
        max_tokens: int = 4000,
        top_p: float = 0.8
    ):
        """
        BaseAgent 초기화
        
        Args:
            system_prompt: 시스템 프롬프트
            model: 사용할 모델명
            temperature: 모델 temperature
            max_tokens: 최대 토큰 수
            top_p: top-p 샘플링 값
        """
        self.system_prompt = system_prompt
        self.model_name = model
        
        # OpenAI API 키 설정 확인
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
            
        # 모델 초기화
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            api_key=openai_api_key
        )
        
        # 기본 프롬프트 템플릿 설정
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])
        
        # 에이전트 상태 초기화
        self.state = {
            "history": []  # 대화 기록
        }
    
    def update_state(self, key: str, value: Any) -> None:
        """
        에이전트 상태 업데이트
        
        Args:
            key: 상태 키
            value: 상태 값
        """
        self.state[key] = value
    
    def get_state(self, key: str = None) -> Any:
        """
        에이전트 상태 조회
        
        Args:
            key: 조회할 상태 키 (None이면 전체 상태 반환)
            
        Returns:
            Any: 상태 값 또는 전체 상태
        """
        if key is None:
            return self.state
        return self.state.get(key)
    
    def add_to_history(self, role: str, content: str) -> None:
        """
        대화 기록에 메시지 추가
        
        Args:
            role: 메시지 역할 ("user" 또는 "assistant")
            content: 메시지 내용
        """
        self.state["history"].append({"role": role, "content": content})
    
    @abstractmethod
    def run(self, input_text: str, **kwargs) -> str:
        """
        에이전트 실행 (추상 메서드)
        
        Args:
            input_text: 입력 텍스트
            **kwargs: 추가 인자
            
        Returns:
            str: 에이전트 응답
        """
        pass 