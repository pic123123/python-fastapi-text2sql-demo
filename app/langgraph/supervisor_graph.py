"""
Supervisor Graph - langgraph-supervisor를 사용한 간단한 구현
"""
from langgraph_supervisor import create_supervisor
from app.services.bedrock import get_bedrock_llm
from app.langgraph.agents.workers import create_worker_agents


def create_supervisor_graph():
    """
    langgraph-supervisor를 사용하여 Supervisor 그래프를 생성합니다.
    
    Returns:
        컴파일 가능한 StateGraph
    """
    model = get_bedrock_llm()
    
    # Worker 에이전트 생성
    sql_agent, research_agent, analysis_agent = create_worker_agents()
    
    # Supervisor 생성
    workflow = create_supervisor(
        agents=[sql_agent, research_agent, analysis_agent],
        model=model,
        prompt=(
            "당신은 팀 슈퍼바이저입니다. "
            "SQL 전문가, 리서치 전문가, 데이터 분석 전문가를 관리합니다.\n\n"
            "작업 할당 가이드:\n"
            "- SQL 쿼리가 필요한 경우: sql_expert 사용\n"
            "- 정보 수집이 필요한 경우: research_expert 사용\n"
            "- 데이터 분석이 필요한 경우: analysis_expert 사용\n\n"
            "**반드시 한국어로 응답하세요.**"
        ),
        output_mode="last_message"  # 마지막 메시지만 포함 (간결한 응답)
    )
    
    return workflow
