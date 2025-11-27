# LangGraph Supervisor 라이브러리 마이그레이션 계획

## 개요

현재 직접 구현한 Planner-Supervisor 아키텍처를 공식 `langgraph-supervisor` 라이브러리로 마이그레이션합니다. 이를 통해 코드를 대폭 간소화하고 공식 지원을 받을 수 있습니다.

## 현재 구현 vs langgraph-supervisor

### 현재 구현 (직접 구현)
- ❌ 복잡한 StateGraph 수동 구성
- ❌ 수동 라우팅 로직
- ❌ 많은 보일러플레이트 코드
- ✅ 완전한 제어

### langgraph-supervisor 사용
- ✅ `create_supervisor()` 한 줄로 구현
- ✅ Tool-based handoff 자동 처리
- ✅ 공식 지원 및 업데이트
- ✅ 간단한 코드

## Proposed Changes

### Dependencies

#### [MODIFY] [pyproject.toml](file:///Users/playauto/Documents/GitHub/python-fastapi/pyproject.toml)

`langgraph-supervisor` 라이브러리 추가:
```toml
dependencies = [
    "langgraph-supervisor>=0.0.31",
    ...
]
```

---

### Core Implementation

#### [NEW] [agents/workers.py](file:///Users/playauto/Documents/GitHub/python-fastapi/app/langgraph/agents/workers.py)

기존 3개 에이전트를 `create_react_agent`로 재구현:
- SQL Agent: SQL 쿼리 생성 도구 포함
- Research Agent: 정보 수집 도구 포함  
- Analysis Agent: 데이터 분석 도구 포함

각 에이전트는 간단한 도구 함수로 정의되고 `create_react_agent`로 생성됩니다.

#### [NEW] [supervisor_graph.py](file:///Users/playauto/Documents/GitHub/python-fastapi/app/langgraph/supervisor_graph.py)

`create_supervisor`를 사용한 간단한 구현:
```python
from langgraph_supervisor import create_supervisor

workflow = create_supervisor(
    [sql_agent, research_agent, analysis_agent],
    model=model,
    prompt="한국어로 응답하는 팀 슈퍼바이저...",
    output_mode="last_message"
)
```

#### [MODIFY] [main.py](file:///Users/playauto/Documents/GitHub/python-fastapi/app/main.py)

새로운 supervisor 그래프 사용:
- 기존 `/agentic-query` 엔드포인트 유지
- 새로운 supervisor 그래프로 교체
- 응답 형식 간소화

---

### Cleanup

#### [DELETE] 기존 복잡한 파일들

다음 파일들은 더 이상 필요하지 않음:
- `app/langgraph/state.py` - langgraph-supervisor가 자동 처리
- `app/langgraph/agents/planner.py` - supervisor가 자동으로 라우팅
- `app/langgraph/agents/supervisor.py` - create_supervisor로 대체
- `app/langgraph/agents/workers/sql_agent.py` - workers.py로 통합
- `app/langgraph/agents/workers/research_agent.py` - workers.py로 통합
- `app/langgraph/agents/workers/analysis_agent.py` - workers.py로 통합
- `app/langgraph/graph.py` - supervisor_graph.py로 대체

---

## 코드 비교

### Before (직접 구현)
```python
# 복잡한 StateGraph 구성
workflow = StateGraph(AgentState)
workflow.add_node("planner", planner_node)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("sql_agent", sql_agent_node)
# ... 많은 노드와 엣지 정의
workflow.add_conditional_edges(...)
# 총 ~300줄 이상
```

### After (langgraph-supervisor)
```python
# 간단한 supervisor 생성
workflow = create_supervisor(
    [sql_agent, research_agent, analysis_agent],
    model=model,
    prompt="슈퍼바이저 프롬프트"
)
# 총 ~50줄
```

## Verification Plan

### 1. 의존성 설치
```bash
uv sync
```

### 2. 서버 실행
```bash
uvicorn app.main:app --reload --port 8000
```

### 3. API 테스트
```bash
curl -X POST http://localhost:8000/agentic-query \
  -H "Content-Type: application/json" \
  -d '{"question": "저번달 가입자 알려줘"}'
```

**예상 결과:**
- 한국어 응답
- SQL 쿼리 생성
- 간결한 최종 답변

### 4. 기능 검증
- [ ] Supervisor가 올바른 에이전트 선택
- [ ] 에이전트 간 정보 전달
- [ ] 한국어 응답 생성
- [ ] 에러 처리

## 구현 순서

1. ✅ 의존성 추가
2. Worker 에이전트 재구현 (도구 기반)
3. Supervisor 생성
4. FastAPI 엔드포인트 업데이트
5. 기존 파일 제거
6. 테스트 및 검증
7. 문서 업데이트
