from fastapi import FastAPI
from pydantic import BaseModel
from app.langgraph.supervisor_graph import create_supervisor_graph


class QueryRequest(BaseModel):
    question: str


app = FastAPI()

# langgraph-supervisor를 사용한 새로운 그래프
supervisor_graph = create_supervisor_graph()
agentic_app = supervisor_graph.compile()


@app.get("/")
async def root():
    return {
        "message": "LangGraph Supervisor API",
        "description": "langgraph-supervisor 라이브러리를 사용한 Multi-Agent 시스템",
        "endpoints": {
            "/agentic-query": "Supervisor가 관리하는 Multi-Agent 시스템"
        }
    }


@app.post("/agentic-query")
async def agentic_query(req: QueryRequest):
    """
    langgraph-supervisor를 사용한 Multi-Agent 엔드포인트
    
    Supervisor가 자동으로 적절한 에이전트를 선택하고 조율합니다.
    """
    try:
        # 그래프 실행
        result = agentic_app.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": req.question
                }
            ]
        })
        
        # 메시지 추출
        messages = result.get("messages", [])
        
        # 최종 답변 (마지막 메시지)
        final_answer = ""
        if messages:
            last_message = messages[-1]
            final_answer = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        return {
            "question": req.question,
            "final_answer": final_answer,
            "message_count": len(messages),
        }
    except Exception as e:
        return {
            "question": req.question,
            "error": f"Execution error: {str(e)}",
            "final_answer": None,
        }
