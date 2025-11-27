"""
Planner-Supervisor 아키텍처를 사용한 LangGraph 그래프 정의
"""
from langgraph.graph import StateGraph, END
from app.langgraph.state import AgentState
from app.langgraph.agents.planner import planner_node
from app.langgraph.agents.supervisor import (
    supervisor_node,
    route_to_agent,
    increment_step_node,
    finalize_node,
)
from app.langgraph.agents.workers.sql_agent import sql_agent_node
from app.langgraph.agents.workers.research_agent import research_agent_node
from app.langgraph.agents.workers.analysis_agent import analysis_agent_node


def create_agentic_graph():
    """
    Planner-Supervisor 아키텍처 그래프 생성
    
    그래프 흐름:
    1. Planner: 사용자 질문 분석 및 실행 계획 생성
    2. Supervisor: 계획의 각 단계를 순차적으로 실행
    3. Worker Agents: 할당된 작업 수행
    4. Increment Step: 다음 단계로 진행
    5. Finalize: 모든 출력을 종합하여 최종 답변 생성
    
    Returns:
        컴파일된 LangGraph
    """
    # StateGraph 생성
    workflow = StateGraph(AgentState)
    
    # 노드 추가
    workflow.add_node("planner", planner_node)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("sql_agent", sql_agent_node)
    workflow.add_node("research_agent", research_agent_node)
    workflow.add_node("analysis_agent", analysis_agent_node)
    workflow.add_node("increment_step", increment_step_node)
    workflow.add_node("finalize", finalize_node)
    
    # 시작점 설정
    workflow.set_entry_point("planner")
    
    # 엣지 정의
    # Planner -> Supervisor
    workflow.add_edge("planner", "supervisor")
    
    # Supervisor -> Worker Agents (조건부 라우팅)
    workflow.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "sql_agent": "sql_agent",
            "research_agent": "research_agent",
            "analysis_agent": "analysis_agent",
            "finalize": "finalize",
        }
    )
    
    # Worker Agents -> Increment Step
    workflow.add_edge("sql_agent", "increment_step")
    workflow.add_edge("research_agent", "increment_step")
    workflow.add_edge("analysis_agent", "increment_step")
    
    # Increment Step -> Supervisor (다시 라우팅) 또는 Finalize
    workflow.add_conditional_edges(
        "increment_step",
        route_to_agent,
        {
            "sql_agent": "sql_agent",
            "research_agent": "research_agent",
            "analysis_agent": "analysis_agent",
            "supervisor": "supervisor",
            "finalize": "finalize",
        }
    )
    
    # Finalize -> END
    workflow.add_edge("finalize", END)
    
    return workflow.compile()


# 기존 그래프 유지 (하위 호환성)
from typing import TypedDict, Optional
from app.services.bedrock import get_bedrock_llm


class SQLState(TypedDict):
    question: str
    schema: str
    sql: Optional[str]
    error: Optional[str]
    result: Optional[str]


def generate_sql(state: SQLState):
    llm = get_bedrock_llm()
    prompt = f"""
    You convert natural language to SQL.
    Schema:
    {state["schema"]}

    Question:
    {state["question"]}

    Output only SQL.
    """
    resp = llm.invoke(prompt)
    return {"sql": resp.content[0].text}


def validate_sql(state: SQLState):
    # TODO: sqlglot로 파싱하고 스키마 검증
    return state


def finalize(state: SQLState):
    return {"result": state["sql"]}


def create_graph():
    """기존 text-to-sql 그래프 (하위 호환성 유지)"""
    workflow = StateGraph(SQLState)

    workflow.add_node("generate_sql", generate_sql)
    workflow.add_node("validate_sql", validate_sql)
    workflow.add_node("finalize", finalize)

    workflow.set_entry_point("generate_sql")

    workflow.add_edge("generate_sql", "validate_sql")
    workflow.add_edge("validate_sql", "finalize")
    workflow.add_edge("finalize", END)

    return workflow.compile()
