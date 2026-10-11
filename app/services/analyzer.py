from typing import List, Dict, Any

def calculate_summary(data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not data_list:
        return {
            "period": "N/A",
            "count": 0,
            "metrics": {"total": 0, "average": 0, "max": 0, "min": 0},
            "trend": "데이터 없음"
        }

    # 날짜 순 정렬
    sorted_data = sorted(data_list, key=lambda x: x["date"])
    dates = [d["date"] for d in sorted_data]
    values = [float(d["value"]) for d in sorted_data]

    total_val = sum(values)
    avg_val = round(total_val / len(values), 2)
    max_val = max(values)
    min_val = min(values)

    # 추세 분석: 전반부와 후반부 평균 비교
    mid = len(values) // 2
    first_half_avg = sum(values[:mid]) / len(values[:mid]) if mid > 0 else avg_val
    second_half_avg = sum(values[mid:]) / len(values[mid:]) if mid > 0 else avg_val

    if second_half_avg > first_half_avg * 1.05:
        trend = "상승 추세"
    elif second_half_avg < first_half_avg * 0.95:
        trend = "하락 추세"
    else:
        trend = "유지/보수적 추세"

    return {
        "period": f"{dates[0]} ~ {dates[-1]}",
        "count": len(sorted_data),
        "metrics": {
            "total": round(total_val, 2),
            "average": avg_val,
            "max": max_val,
            "min": min_val
        },
        "trend": trend
    }