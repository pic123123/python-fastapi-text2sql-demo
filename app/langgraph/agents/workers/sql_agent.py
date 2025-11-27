"""
SQL Agent - 자연어를 SQL로 변환하고 검증하는 Worker 에이전트
"""
from typing import Dict, Any
from app.services.bedrock import get_bedrock_llm
from app.langgraph.state import AgentState


def sql_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    SQL Agent 노드
    
    사용자의 자연어 질문을 SQL 쿼리로 변환합니다.
    
    Args:
        state: 현재 AgentState
        
    Returns:
        업데이트할 상태 딕셔너리
    """
    llm = get_bedrock_llm()
    
    # 기본 스키마 정의 (실제로는 동적으로 가져와야 함)
    schema = """
    CREATE TABLE user (
        user_id INT PRIMARY KEY,
        email VARCHAR(255),
        created_at DATETIME
    );
    """
    
    # 이전 에이전트의 출력이 있다면 컨텍스트에 포함
    context = ""
    if state.get("agent_outputs"):
        context = "\n\nPrevious agent outputs:\n"
        for agent_name, output in state["agent_outputs"].items():
            context += f"- {agent_name}: {output}\n"
    
    prompt = f"""당신은 SQL 전문가입니다. 자연어 질문을 SQL 쿼리로 변환하세요.

데이터베이스 스키마:
{schema}

질문: {state["question"]}
{context}

지시사항:
1. 스키마를 기반으로 유효한 SQL 쿼리를 생성하세요
2. 올바른 SQL 문법을 사용하세요
3. SQL 쿼리만 출력하세요
4. 주어진 스키마로 질문에 답할 수 없다면 한국어로 이유를 설명하세요

**반드시 한국어로 응답하세요.**

SQL 쿼리:"""
    
    try:
        response = llm.invoke(prompt)
        sql_output = response.content
        
        # 텍스트 응답인 경우 처리
        if isinstance(sql_output, list):
            sql_output = sql_output[0].text if hasattr(sql_output[0], 'text') else str(sql_output[0])
        
        # 에이전트 출력 업데이트
        updated_outputs = state.get("agent_outputs", {}).copy()
        updated_outputs["sql_agent"] = sql_output
        
        return {
            "agent_outputs": updated_outputs,
            "next_agent": None,  # Supervisor가 결정
        }
    except Exception as e:
        return {
            "error": f"SQL Agent error: {str(e)}",
            "next_agent": None,
        }


def execute_sql_node(state: AgentState) -> Dict[str, Any]:
    """
    SQL 실행 노드 (선택적)
    
    생성된 SQL을 실제로 실행합니다.
    현재는 placeholder로, 실제 DB 연결 시 구현 필요
    
    Args:
        state: 현재 AgentState
        
    Returns:
        업데이트할 상태 딕셔너리
    """
    sql_query = state.get("agent_outputs", {}).get("sql_agent", "")
    
    # TODO: 실제 DB 연결 및 쿼리 실행
    # 현재는 시뮬레이션
    result = f"[Simulated] Would execute: {sql_query}"
    
    updated_outputs = state.get("agent_outputs", {}).copy()
    updated_outputs["sql_execution"] = result
    
    return {
        "agent_outputs": updated_outputs,
    }
