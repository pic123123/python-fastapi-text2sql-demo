"""
Planner Agent - 사용자 요청을 분석하고 실행 계획을 생성하는 에이전트
"""
from typing import Dict, Any, List
import json
from app.services.bedrock import get_bedrock_llm
from app.langgraph.state import AgentState


def planner_node(state: AgentState) -> Dict[str, Any]:
    """
    Planner Agent 노드
    
    사용자의 질문을 분석하고 단계별 실행 계획을 생성합니다.
    
    Args:
        state: 현재 AgentState
        
    Returns:
        업데이트할 상태 딕셔너리
    """
    llm = get_bedrock_llm()
    
    prompt = f"""당신은 계획 에이전트입니다. 사용자의 질문을 분석하고 단계별 실행 계획을 생성하세요.

사용 가능한 에이전트:
1. sql_agent: 자연어를 SQL 쿼리로 변환하고 데이터베이스 작업 수행
2. research_agent: 정보 수집 및 컨텍스트 제공
3. analysis_agent: 데이터 분석 및 인사이트 도출

사용자 질문: {state["question"]}

다음 형식으로 계획을 생성하세요 (반드시 유효한 JSON만 응답):
{{
    "steps": [
        {{
            "step": 1,
            "description": "수행할 작업에 대한 간단한 설명 (한국어)",
            "agent": "agent_name"
        }},
        ...
    ]
}}

가이드라인:
- 계획을 간결하게 유지하세요 (일반적으로 2-4단계)
- 각 단계에 가장 적합한 에이전트를 선택하세요
- 단계 간 종속성을 고려하세요
- SQL 관련 질문은 sql_agent 사용
- 분석 질문은 데이터를 얻은 후 analysis_agent 사용
- 일반 정보는 research_agent 사용
- description은 반드시 한국어로 작성하세요

계획 (JSON만):"""
    
    try:
        response = llm.invoke(prompt)
        plan_text = response.content
        
        # 텍스트 응답인 경우 처리
        if isinstance(plan_text, list):
            plan_text = plan_text[0].text if hasattr(plan_text[0], 'text') else str(plan_text[0])
        
        # JSON 파싱
        # 코드 블록이 있다면 제거
        if "```json" in plan_text:
            plan_text = plan_text.split("```json")[1].split("```")[0].strip()
        elif "```" in plan_text:
            plan_text = plan_text.split("```")[1].split("```")[0].strip()
        
        plan_data = json.loads(plan_text)
        plan_steps = plan_data.get("steps", [])
        
        # 첫 번째 단계의 에이전트를 다음 에이전트로 설정
        next_agent = plan_steps[0]["agent"] if plan_steps else None
        
        return {
            "plan": plan_steps,
            "current_step": 0,
            "next_agent": next_agent,
            "agent_outputs": {},
        }
    except json.JSONDecodeError as e:
        # JSON 파싱 실패 시 기본 계획 생성
        default_plan = [
            {
                "step": 1,
                "description": "Process the user's question",
                "agent": "sql_agent"  # 기본값
            }
        ]
        return {
            "plan": default_plan,
            "current_step": 0,
            "next_agent": "sql_agent",
            "agent_outputs": {},
            "error": f"Plan parsing error: {str(e)}. Using default plan."
        }
    except Exception as e:
        return {
            "error": f"Planner error: {str(e)}",
            "plan": [],
            "current_step": 0,
            "next_agent": None,
        }
