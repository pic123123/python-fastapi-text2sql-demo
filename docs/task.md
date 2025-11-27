# LangGraph Planner-Supervisor Agentic AI 구축

## 목표
LangGraph를 사용하여 planner 기반 supervisor 아키텍처를 구현한 Agentic AI 시스템 구축

## 작업 항목

### 분석 및 계획
- [x] 기존 코드 구조 분석
- [x] Planner-Supervisor 아키텍처 설계
- [x] 필요한 에이전트 및 도구 정의

### 구현
- [x] State 스키마 정의 (`state.py`)
- [x] Worker 에이전트 구현
  - [x] SQL Agent (`agents/workers/sql_agent.py`)
  - [x] Research Agent (`agents/workers/research_agent.py`)
  - [x] Analysis Agent (`agents/workers/analysis_agent.py`)
- [x] Planner 에이전트 구현 (`agents/planner.py`)
- [x] Supervisor 에이전트 구현 (`agents/supervisor.py`)
- [x] 그래프 재구성 (`graph.py`)
- [x] FastAPI 엔드포인트 추가 (`main.py`)
- [x] 도구 정의 (`tools.py`)

### 검증
- [x] 단위 테스트 작성
- [x] 통합 테스트 실행
- [x] 수동 검증
- [x] 문서화
