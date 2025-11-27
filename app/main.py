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
        
        # 에이전트별 응답 추출
        agent_responses = []
        final_answer = ""
        
        for i, msg in enumerate(messages):
            # 메시지 타입 확인
            msg_type = getattr(msg, 'type', None) or (msg.get('type') if isinstance(msg, dict) else None)
            
            # AI 메시지만 처리
            if msg_type == 'ai':
                content = getattr(msg, 'content', '') or (msg.get('content', '') if isinstance(msg, dict) else str(msg))
                
                # 에이전트 이름 추출
                agent_name = "supervisor"
                
                # Tool calls 확인 (어떤 에이전트를 호출했는지)
                tool_calls = getattr(msg, 'tool_calls', None) or (msg.get('tool_calls') if isinstance(msg, dict) else None)
                if tool_calls and len(tool_calls) > 0:
                    tool_name = tool_calls[0].get('name', '') if isinstance(tool_calls[0], dict) else getattr(tool_calls[0], 'name', '')
                    if 'sql' in tool_name.lower():
                        agent_name = "supervisor → sql_expert"
                    elif 'research' in tool_name.lower():
                        agent_name = "supervisor → research_expert"
                    elif 'analysis' in tool_name.lower():
                        agent_name = "supervisor → analysis_expert"
                
                # 이전 메시지가 tool이면 해당 tool의 에이전트
                if i > 0:
                    prev_msg = messages[i-1]
                    prev_type = getattr(prev_msg, 'type', None) or (prev_msg.get('type') if isinstance(prev_msg, dict) else None)
                    if prev_type == 'tool':
                        tool_name = getattr(prev_msg, 'name', '') or (prev_msg.get('name', '') if isinstance(prev_msg, dict) else '')
                        if 'sql' in tool_name.lower():
                            agent_name = "sql_expert"
                        elif 'research' in tool_name.lower():
                            agent_name = "research_expert"
                        elif 'analysis' in tool_name.lower():
                            agent_name = "analysis_expert"
                
                if content and content.strip():
                    agent_responses.append({
                        "agent": agent_name,
                        "response": content
                    })
                    
                    # 마지막 의미있는 응답을 final_answer로
                    if content.strip() and "Transferring" not in content:
                        final_answer = content
        
        # final_answer가 비어있으면 마지막 응답 사용
        if not final_answer and agent_responses:
            final_answer = agent_responses[-1]["response"]
        
        return {
            "question": req.question,
            "final_answer": final_answer,
            "agent_responses": agent_responses,
            "message_count": len(messages),
        }
    except Exception as e:
        return {
            "question": req.question,
            "error": f"Execution error: {str(e)}",
            "final_answer": None,
        }
