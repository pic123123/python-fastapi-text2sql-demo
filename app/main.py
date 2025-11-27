from fastapi import FastAPI
from pydantic import BaseModel
from app.langgraph.graph import create_graph, create_agentic_graph


class QueryRequest(BaseModel):
    question: str


app = FastAPI()

# 기존 그래프 (하위 호환성)
graph = create_graph()

# 새로운 Planner-Supervisor 그래프
agentic_graph = create_agentic_graph()


@app.get("/")
async def root():
    return {
        "message": "LangGraph Planner-Supervisor API",
        "endpoints": {
            "/text-to-sql": "Legacy text-to-sql endpoint",
            "/agentic-query": "New planner-supervisor agentic endpoint"
        }
    }


@app.post("/text-to-sql")
async def text_to_sql(req: QueryRequest):
    """기존 text-to-sql 엔드포인트 (하위 호환성 유지)"""
    state = {
        "question": req.question,
        "schema": """
        CREATE TABLE user (
            user_id INT,
            email VARCHAR(255),
            created_at DATETIME
        );
    """,
        "sql": None,
        "error": None,
        "result": None,
    }

    result = graph.invoke(state)
    return {"result": result.get("result", None), "state": result}


@app.post("/agentic-query")
async def agentic_query(req: QueryRequest):
    """
    새로운 Planner-Supervisor 아키텍처 엔드포인트
    
    사용자의 질문을 분석하고, 실행 계획을 생성한 후,
    적절한 에이전트들을 조율하여 최종 답변을 제공합니다.
    """
    # 초기 상태 설정
    initial_state = {
        "question": req.question,
        "messages": [],
        "plan": None,
        "current_step": 0,
        "agent_outputs": {},
        "final_answer": None,
        "error": None,
        "next_agent": None,
        "is_complete": False,
    }
    
    try:
        # 그래프 실행
        result = agentic_graph.invoke(initial_state)
        
        return {
            "question": req.question,
            "plan": result.get("plan", []),
            "agent_outputs": result.get("agent_outputs", {}),
            "final_answer": result.get("final_answer", "No answer generated"),
            "error": result.get("error"),
        }
    except Exception as e:
        return {
            "question": req.question,
            "error": f"Execution error: {str(e)}",
            "final_answer": None,
        }

