import os
import time
from typing import List, Dict, Any, Optional
import json

# Brave 패키지의 올바른 import 방법으로 변경
from brave import Brave
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class WebSearchTool:
    """웹 검색 도구"""
    
    def __init__(self):
        """웹 검색 도구 초기화"""
        self.api_key = os.getenv("BRAVE_API_KEY")
        # Brave 객체 초기화 방법 변경
        self.client = Brave(api_key=self.api_key) if self.api_key else None
        self.use_dummy_data = not self.api_key
    
    def search(self, query: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        웹 검색을 수행합니다.
        
        Args:
            query: 검색 쿼리
            count: 검색 결과 수
            
        Returns:
            List[Dict[str, Any]]: 검색 결과 목록
        """
        if self.use_dummy_data:
            return self._get_dummy_results(query, count)
        
        try:
            # Brave 최신 API에 맞게 메서드 호출 방식 변경
            search_results = self.client.search(q=query, count=count)
            results = []
            
            # 결과 구조에 맞게 파싱 방식 수정
            for item in search_results.web_results:
                results.append({
                    "title": item.title,
                    "url": item.url,
                    "description": item.description
                })
            
            return results
        except Exception as e:
            print(f"검색 중 오류 발생: {str(e)}")
            return self._get_dummy_results(query, count)
    
    def search_field(self, field: str, aspect: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        특정 기술 분야와 측면에 대한 검색을 수행합니다.
        
        Args:
            field: 기술 분야 (예: "ai", "robotics")
            aspect: 검색 측면 (예: "research_paper", "patents", "news", "investment")
            count: 검색 결과 수
        
        Returns:
            List[Dict[str, Any]]: 검색 결과 목록
        """
        # 검색 쿼리 생성
        queries = {
            "research_paper": f"latest research papers {field} technology 2025 future trends",
            "patents": f"recent patents {field} technology innovation trends",
            "news": f"recent {field} technology news breakthrough development",
            "investment": f"{field} technology venture capital investment trends",
            "corporate_rd": f"major companies {field} technology R&D investment focus"
        }
        
        query = queries.get(aspect, f"{field} technology {aspect} trends")
        
        # 검색 실행
        results = self.search(query, count)
        
        # 결과에 메타데이터 추가
        for result in results:
            result["field"] = field
            result["aspect"] = aspect
        
        return results
    
    def analyze_trends(self, field: str) -> Dict[str, Any]:
        """
        특정 기술 분야의 트렌드를 분석하기 위한 데이터를 수집합니다.
        
        Args:
            field: 기술 분야 (예: "ai", "robotics")
            
        Returns:
            Dict[str, Any]: 분석된 트렌드 데이터
        """
        # 다양한 측면에서 검색 수행
        aspects = ["research_paper", "patents", "news", "investment", "corporate_rd"]
        results = {}
        
        for aspect in aspects:
            results[aspect] = self.search_field(field, aspect, count=5)
            time.sleep(1)  # API 호출 간 딜레이
        
        return results
    
    def _get_dummy_results(self, query: str, count: int) -> List[Dict[str, Any]]:
        """
        API 키가 없을 때 사용할 더미 검색 결과를 반환합니다.
        
        Args:
            query: 검색 쿼리
            count: 결과 수
            
        Returns:
            List[Dict[str, Any]]: 더미 검색 결과
        """
        dummy_results = [
            {
                "title": f"미래 기술 트렌드: {query}에 관한 연구",
                "url": "https://example.com/research/1",
                "description": f"{query}에 관한 최신 연구 동향을 분석한 결과, 향후 5년간 급격한 발전이 예상됩니다."
            },
            {
                "title": f"{query} 기술의 산업적 영향 분석",
                "url": "https://example.com/impact/2",
                "description": f"{query} 기술이 다양한 산업에 미치는 영향을 분석하고, 미래 비즈니스 기회를 탐색합니다."
            },
            {
                "title": f"최신 {query} 특허 동향 보고서",
                "url": "https://example.com/patents/3",
                "description": f"지난 2년간 {query} 관련 특허 출원 동향을 분석하여 주요 혁신 트렌드를 파악합니다."
            },
            {
                "title": f"{query} 스타트업 투자 동향",
                "url": "https://example.com/investment/4",
                "description": f"{query} 분야 스타트업에 대한 벤처 캐피털 투자 동향과 주요 플레이어를 분석합니다."
            },
            {
                "title": f"기업의 {query} R&D 전략",
                "url": "https://example.com/strategy/5",
                "description": f"주요 기업들의 {query} 분야 R&D 투자 전략과 주력 개발 방향을 조사했습니다."
            }
        ]
        
        return dummy_results[:min(count, len(dummy_results))] 