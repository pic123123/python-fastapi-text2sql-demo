"""
더미 데이터 및 SQL 실행 기능
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any


# 더미 사용자 데이터
DUMMY_USERS = [
    {"user_id": 1, "email": "user1@example.com", "created_at": "2024-10-15 10:30:00"},
    {"user_id": 2, "email": "user2@example.com", "created_at": "2024-10-20 14:22:00"},
    {"user_id": 3, "email": "user3@example.com", "created_at": "2024-10-25 09:15:00"},
    {"user_id": 4, "email": "user4@example.com", "created_at": "2024-10-28 16:45:00"},
    {"user_id": 5, "email": "user5@example.com", "created_at": "2024-11-02 11:20:00"},
    {"user_id": 6, "email": "user6@example.com", "created_at": "2024-11-05 13:30:00"},
    {"user_id": 7, "email": "user7@example.com", "created_at": "2024-11-10 15:10:00"},
    {"user_id": 8, "email": "user8@example.com", "created_at": "2024-11-15 08:50:00"},
    {"user_id": 9, "email": "user9@example.com", "created_at": "2024-11-20 12:40:00"},
    {"user_id": 10, "email": "user10@example.com", "created_at": "2024-11-25 17:25:00"},
]


def execute_dummy_sql(sql_query: str) -> List[Dict[str, Any]]:
    """
    더미 데이터에 대해 간단한 SQL 쿼리를 실행합니다.
    
    Args:
        sql_query: SQL 쿼리 문자열
        
    Returns:
        쿼리 결과 (딕셔너리 리스트)
    """
    sql_lower = sql_query.lower()
    
    # COUNT 쿼리
    if "count(*)" in sql_lower or "count(1)" in sql_lower:
        # 지난달 필터링
        if "interval 1 month" in sql_lower or "저번" in sql_lower or "지난" in sql_lower:
            # 현재 날짜 기준 지난달 계산
            today = datetime.now()
            first_day_this_month = today.replace(day=1)
            last_day_last_month = first_day_this_month - timedelta(days=1)
            first_day_last_month = last_day_last_month.replace(day=1)
            
            count = 0
            for user in DUMMY_USERS:
                created = datetime.strptime(user["created_at"], "%Y-%m-%d %H:%M:%S")
                if first_day_last_month <= created <= last_day_last_month:
                    count += 1
            
            return [{"count": count}]
        else:
            return [{"count": len(DUMMY_USERS)}]
    
    # SELECT * 쿼리
    elif "select *" in sql_lower or "select" in sql_lower:
        # 지난달 필터링
        if "interval 1 month" in sql_lower or "저번" in sql_lower or "지난" in sql_lower:
            today = datetime.now()
            first_day_this_month = today.replace(day=1)
            last_day_last_month = first_day_this_month - timedelta(days=1)
            first_day_last_month = last_day_last_month.replace(day=1)
            
            results = []
            for user in DUMMY_USERS:
                created = datetime.strptime(user["created_at"], "%Y-%m-%d %H:%M:%S")
                if first_day_last_month <= created <= last_day_last_month:
                    results.append(user)
            
            return results
        else:
            return DUMMY_USERS
    
    # 기본값
    return DUMMY_USERS


def format_sql_result(result: List[Dict[str, Any]]) -> str:
    """
    SQL 결과를 한국어로 포맷팅합니다.
    
    Args:
        result: SQL 실행 결과
        
    Returns:
        포맷팅된 결과 문자열
    """
    if not result:
        return "결과가 없습니다."
    
    # COUNT 결과
    if len(result) == 1 and "count" in result[0]:
        return f"총 {result[0]['count']}명의 사용자가 있습니다."
    
    # 사용자 목록
    output = f"총 {len(result)}명의 사용자:\n\n"
    for user in result:
        output += f"- ID: {user['user_id']}, 이메일: {user['email']}, 가입일: {user['created_at']}\n"
    
    return output
