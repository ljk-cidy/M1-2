import math
from typing import List, Dict, Any

def calculate_summary(data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not data_list:
        return {
            "period": "N/A", "count": 0,
            "metrics": {"total": 0, "average": 0, "max": 0, "min": 0, "std_dev": 0, "recent_7d_avg": 0},
            "trend": "데이터 없음"
        }

    sorted_data = sorted(data_list, key=lambda x: x.get("date", ""))
    dates = [d["date"] for d in sorted_data if "date" in d]
    values = [float(d["value"]) for d in sorted_data if "value" in d]

    total_val = sum(values)
    avg_val = round(total_val / len(values), 2)
    
    # 추가 지표 1: 표준편차 (변동성)
    variance = sum((x - avg_val) ** 2 for x in values) / len(values)
    std_dev = round(math.sqrt(variance), 2)

    # 추가 지표 2: 최근 7개 데이터 평균
    recent_7d = values[-7:] if len(values) >= 7 else values
    recent_7d_avg = round(sum(recent_7d) / len(recent_7d), 2)

    return {
        "period": f"{dates[0]} ~ {dates[-1]}",
        "count": len(sorted_data),
        "metrics": {
            "total": round(total_val, 2),
            "average": avg_val,
            "max": max(values),
            "min": min(values),
            "std_dev": std_dev,
            "recent_7d_avg": recent_7d_avg
        },
        "trend": "상승" if values[-1] > avg_val else "하락/유지"
    }