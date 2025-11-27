"""
Research Agent - 정보 검색 및 조사를 수행하는 Worker 에이전트
"""
from typing import Dict, Any
from app.services.bedrock import get_bedrock_llm
from app.langgraph.state import AgentState


def research_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    Research Agent 노드
    
    주어진 주제에 대한 정보를 수집하고 분석합니다.
    
    Args:
        state: 현재 AgentState
        
    Returns:
        업데이트할 상태 딕셔너리
    """
    llm = get_bedrock_llm()
    
    # 이전 에이전트의 출력이 있다면 컨텍스트에 포함
    context = ""
    if state.get("agent_outputs"):
        context = "\n\nPrevious agent outputs:\n"
        for agent_name, output in state["agent_outputs"].items():
            context += f"- {agent_name}: {output}\n"
    
    prompt = f"""당신은 리서치 어시스턴트입니다. 정보를 수집하고 종합하는 것이 당신의 임무입니다.

질문: {state["question"]}
{context}

지시사항:
1. 질문을 분석하고 핵심 주제를 파악하세요
2. 관련된 정보, 사실, 인사이트를 제공하세요
3. 응답을 명확하게 구조화하세요
4. 다른 에이전트의 데이터가 필요하면 무엇이 필요한지 언급하세요

**반드시 한국어로 응답하세요.**

리서치 결과:"""
    
    try:
        response = llm.invoke(prompt)
        research_output = response.content
        
        # 텍스트 응답인 경우 처리
        if isinstance(research_output, list):
            research_output = research_output[0].text if hasattr(research_output[0], 'text') else str(research_output[0])
        
        # 에이전트 출력 업데이트
        updated_outputs = state.get("agent_outputs", {}).copy()
        updated_outputs["research_agent"] = research_output
        
        return {
            "agent_outputs": updated_outputs,
            "next_agent": None,  # Supervisor가 결정
        }
    except Exception as e:
        return {
            "error": f"Research Agent error: {str(e)}",
            "next_agent": None,
        }
