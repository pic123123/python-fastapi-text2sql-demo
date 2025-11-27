"""
Analysis Agent - 데이터 분석 및 인사이트 도출 Worker 에이전트
"""
from typing import Dict, Any
from app.services.bedrock import get_bedrock_llm
from app.langgraph.state import AgentState


def analysis_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    Analysis Agent 노드
    
    데이터를 분석하고 인사이트를 도출합니다.
    
    Args:
        state: 현재 AgentState
        
    Returns:
        업데이트할 상태 딕셔너리
    """
    llm = get_bedrock_llm()
    
    # 이전 에이전트의 출력이 있다면 컨텍스트에 포함
    context = ""
    if state.get("agent_outputs"):
        context = "\n\nData from other agents:\n"
        for agent_name, output in state["agent_outputs"].items():
            context += f"- {agent_name}:\n{output}\n\n"
    
    prompt = f"""당신은 데이터 분석가입니다. 데이터를 분석하고 인사이트를 제공하는 것이 당신의 임무입니다.

원래 질문: {state["question"]}
{context}

지시사항:
1. 다른 에이전트로부터 받은 데이터를 분석하세요
2. 패턴, 트렌드, 주요 발견사항을 식별하세요
3. 실행 가능한 인사이트와 권장사항을 제공하세요
4. 분석 결과를 명확하고 구조화된 형식으로 제시하세요
5. 더 많은 데이터가 필요하면 무엇이 부족한지 명시하세요

**반드시 한국어로 응답하세요.**

분석 결과:"""
    
    try:
        response = llm.invoke(prompt)
        analysis_output = response.content
        
        # 텍스트 응답인 경우 처리
        if isinstance(analysis_output, list):
            analysis_output = analysis_output[0].text if hasattr(analysis_output[0], 'text') else str(analysis_output[0])
        
        # 에이전트 출력 업데이트
        updated_outputs = state.get("agent_outputs", {}).copy()
        updated_outputs["analysis_agent"] = analysis_output
        
        return {
            "agent_outputs": updated_outputs,
            "next_agent": None,  # Supervisor가 결정
        }
    except Exception as e:
        return {
            "error": f"Analysis Agent error: {str(e)}",
            "next_agent": None,
        }
