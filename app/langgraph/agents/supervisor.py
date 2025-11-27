"""
Supervisor Agent - 계획을 실행하고 Worker 에이전트를 조율하는 에이전트
"""
from typing import Dict, Any
from app.services.bedrock import get_bedrock_llm
from app.langgraph.state import AgentState


def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """
    Supervisor Agent 노드
    
    계획의 진행 상황을 확인하고 다음 에이전트를 결정합니다.
    
    Args:
        state: 현재 AgentState
        
    Returns:
        업데이트할 상태 딕셔너리
    """
    plan = state.get("plan", [])
    current_step = state.get("current_step", 0)
    
    # 계획이 없거나 모든 단계가 완료된 경우
    if not plan or current_step >= len(plan):
        return {
            "is_complete": True,
            "next_agent": "finalize",
        }
    
    # 다음 단계로 진행
    next_step = plan[current_step]
    next_agent = next_step.get("agent")
    
    return {
        "current_step": current_step,
        "next_agent": next_agent,
    }


def route_to_agent(state: AgentState) -> str:
    """
    다음 에이전트로 라우팅하는 조건부 엣지 함수
    
    Args:
        state: 현재 AgentState
        
    Returns:
        다음 노드의 이름
    """
    next_agent = state.get("next_agent")
    
    # 에러가 있으면 종료
    if state.get("error"):
        return "finalize"
    
    # 완료 상태면 종료
    if state.get("is_complete"):
        return "finalize"
    
    # 다음 에이전트가 지정되어 있으면 해당 에이전트로
    if next_agent:
        return next_agent
    
    # 기본값: supervisor로 돌아가기
    return "supervisor"


def increment_step_node(state: AgentState) -> Dict[str, Any]:
    """
    현재 단계를 증가시키는 노드
    
    Worker 에이전트 실행 후 호출되어 다음 단계로 진행합니다.
    
    Args:
        state: 현재 AgentState
        
    Returns:
        업데이트할 상태 딕셔너리
    """
    current_step = state.get("current_step", 0)
    plan = state.get("plan", [])
    
    # 다음 단계로 증가
    next_step_num = current_step + 1
    
    # 모든 단계가 완료되었는지 확인
    if next_step_num >= len(plan):
        return {
            "current_step": next_step_num,
            "is_complete": True,
            "next_agent": "finalize",
        }
    
    # 다음 단계의 에이전트 결정
    next_step = plan[next_step_num]
    next_agent = next_step.get("agent")
    
    return {
        "current_step": next_step_num,
        "next_agent": next_agent,
    }


def finalize_node(state: AgentState) -> Dict[str, Any]:
    """
    최종 응답을 생성하는 노드
    
    모든 에이전트의 출력을 종합하여 사용자에게 제공할 최종 답변을 생성합니다.
    
    Args:
        state: 현재 AgentState
        
    Returns:
        업데이트할 상태 딕셔너리
    """
    llm = get_bedrock_llm()
    
    # 에러가 있는 경우
    if state.get("error"):
        return {
            "final_answer": f"An error occurred: {state['error']}",
            "is_complete": True,
        }
    
    # 모든 에이전트 출력 수집
    agent_outputs = state.get("agent_outputs", {})
    
    if not agent_outputs:
        return {
            "final_answer": "No outputs were generated from the agents.",
            "is_complete": True,
        }
    
    # 출력 종합
    outputs_text = ""
    for agent_name, output in agent_outputs.items():
        outputs_text += f"\n\n{agent_name}:\n{output}"
    
    prompt = f"""당신은 유용한 어시스턴트입니다. 여러 에이전트의 출력을 명확하고 포괄적인 답변으로 종합하세요.

원래 질문: {state["question"]}

에이전트 출력:{outputs_text}

지시사항:
1. 사용자의 질문에 답하는 일관된 응답을 작성하세요
2. 모든 에이전트의 정보를 통합하세요
3. 명확하고 간결하게 작성하세요
4. SQL 쿼리가 있다면 명확하게 제시하세요
5. 분석 결과가 있다면 주요 인사이트를 강조하세요

**반드시 한국어로 응답하세요.**

최종 답변:"""
    
    try:
        response = llm.invoke(prompt)
        final_text = response.content
        
        # 텍스트 응답인 경우 처리
        if isinstance(final_text, list):
            final_text = final_text[0].text if hasattr(final_text[0], 'text') else str(final_text[0])
        
        return {
            "final_answer": final_text,
            "is_complete": True,
        }
    except Exception as e:
        # LLM 호출 실패 시 에이전트 출력을 그대로 반환
        return {
            "final_answer": f"Agent outputs:\n{outputs_text}",
            "is_complete": True,
            "error": f"Finalize error: {str(e)}"
        }
