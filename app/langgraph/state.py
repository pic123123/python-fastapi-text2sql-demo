from typing import TypedDict, Optional, List, Dict, Any
from langgraph.graph import MessagesState


class AgentState(MessagesState):
    """
    Planner-Supervisor 아키텍처를 위한 전체 시스템 상태
    
    MessagesState를 상속하여 messages 필드를 자동으로 포함
    """
    # 사용자의 원본 질문
    question: str
    
    # Planner가 생성한 실행 계획
    # 각 단계는 {"step": int, "description": str, "agent": str} 형태
    plan: Optional[List[Dict[str, Any]]]
    
    # 현재 실행 중인 단계 번호
    current_step: int
    
    # 각 에이전트의 출력 결과
    # {"agent_name": "output"} 형태로 저장
    agent_outputs: Dict[str, Any]
    
    # 최종 응답
    final_answer: Optional[str]
    
    # 에러 정보 (있는 경우)
    error: Optional[str]
    
    # 다음에 실행할 에이전트 이름
    next_agent: Optional[str]
    
    # 작업 완료 여부
    is_complete: bool
