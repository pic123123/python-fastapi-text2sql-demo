"""
Worker Agents - langgraph-supervisor를 사용한 간단한 에이전트 구현
"""
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from app.services.bedrock import get_bedrock_llm


# SQL 도구 정의
@tool
def generate_sql_query(question: str) -> str:
    """
    자연어 질문을 SQL 쿼리로 변환합니다.
    
    Args:
        question: 사용자의 자연어 질문
        
    Returns:
        생성된 SQL 쿼리
    """
    llm = get_bedrock_llm()
    
    schema = """
    CREATE TABLE user (
        user_id INT PRIMARY KEY,
        email VARCHAR(255),
        created_at DATETIME
    );
    """
    
    prompt = f"""당신은 SQL 전문가입니다. 자연어 질문을 SQL 쿼리로 변환하세요.

데이터베이스 스키마:
{schema}

질문: {question}

지시사항:
1. 스키마를 기반으로 유효한 SQL 쿼리를 생성하세요
2. 올바른 SQL 문법을 사용하세요
3. SQL 쿼리만 출력하세요

**반드시 한국어로 설명과 함께 응답하세요.**

SQL 쿼리:"""
    
    response = llm.invoke(prompt)
    sql_output = response.content
    
    if isinstance(sql_output, list):
        sql_output = sql_output[0].text if hasattr(sql_output[0], 'text') else str(sql_output[0])
    
    return sql_output


# Research 도구 정의
@tool
def research_topic(topic: str) -> str:
    """
    주어진 주제에 대한 정보를 수집하고 분석합니다.
    
    Args:
        topic: 조사할 주제
        
    Returns:
        리서치 결과
    """
    llm = get_bedrock_llm()
    
    prompt = f"""당신은 리서치 전문가입니다. 주어진 주제에 대한 정보를 제공하세요.

주제: {topic}

지시사항:
1. 주제를 분석하고 핵심 내용을 파악하세요
2. 관련된 정보와 인사이트를 제공하세요
3. 응답을 명확하게 구조화하세요

**반드시 한국어로 응답하세요.**

리서치 결과:"""
    
    response = llm.invoke(prompt)
    research_output = response.content
    
    if isinstance(research_output, list):
        research_output = research_output[0].text if hasattr(research_output[0], 'text') else str(research_output[0])
    
    return research_output


# Analysis 도구 정의
@tool
def analyze_data(data: str) -> str:
    """
    데이터를 분석하고 인사이트를 도출합니다.
    
    Args:
        data: 분석할 데이터
        
    Returns:
        분석 결과 및 인사이트
    """
    llm = get_bedrock_llm()
    
    prompt = f"""당신은 데이터 분석 전문가입니다. 주어진 데이터를 분석하고 인사이트를 제공하세요.

데이터:
{data}

지시사항:
1. 데이터를 분석하세요
2. 패턴과 트렌드를 식별하세요
3. 실행 가능한 인사이트를 제공하세요
4. 분석 결과를 명확하게 제시하세요

**반드시 한국어로 응답하세요.**

분석 결과:"""
    
    response = llm.invoke(prompt)
    analysis_output = response.content
    
    if isinstance(analysis_output, list):
        analysis_output = analysis_output[0].text if hasattr(analysis_output[0], 'text') else str(analysis_output[0])
    
    return analysis_output


# Worker 에이전트 생성
def create_worker_agents():
    """
    3개의 전문화된 Worker 에이전트를 생성합니다.
    
    Returns:
        (sql_agent, research_agent, analysis_agent) 튜플
    """
    model = get_bedrock_llm()
    
    # SQL Agent
    sql_agent = create_react_agent(
        model=model,
        tools=[generate_sql_query],
        name="sql_expert",
        prompt=(
            "당신은 SQL 전문가입니다. "
            "자연어 질문을 SQL 쿼리로 변환하는 것이 당신의 임무입니다. "
            "항상 한 번에 하나의 도구만 사용하세요. "
            "**반드시 한국어로 응답하세요.**"
        )
    )
    
    # Research Agent
    research_agent = create_react_agent(
        model=model,
        tools=[research_topic],
        name="research_expert",
        prompt=(
            "당신은 리서치 전문가입니다. "
            "정보를 수집하고 분석하는 것이 당신의 임무입니다. "
            "**반드시 한국어로 응답하세요.**"
        )
    )
    
    # Analysis Agent
    analysis_agent = create_react_agent(
        model=model,
        tools=[analyze_data],
        name="analysis_expert",
        prompt=(
            "당신은 데이터 분석 전문가입니다. "
            "데이터를 분석하고 인사이트를 도출하는 것이 당신의 임무입니다. "
            "**반드시 한국어로 응답하세요.**"
        )
    )
    
    return sql_agent, research_agent, analysis_agent
