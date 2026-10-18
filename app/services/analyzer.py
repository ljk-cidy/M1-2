"""Summarize chronological values and compare half-period averages."""

from statistics import fmean, pstdev
from typing import Any


def calculate_summary(data_list: list[dict[str, Any]]) -> dict[str, Any]:
    """Trend uses a 5% relative threshold, including negative baselines."""
    if not data_list:
        return {
            "period": "N/A",
            "count": 0,
            "metrics": {
                "total": 0,
                "average": 0,
                "max": 0,
                "min": 0,
                "standard_deviation": 0,
            },
            "trend": "데이터 없음",
        }
    items = sorted(data_list, key=lambda item: item["date"])
    values = [float(item["value"]) for item in items]
    mid = len(values) // 2
    trend = "유지 추세"
    if mid:
        first = fmean(values[:mid])
        second = fmean(values[mid:])
        change = second - first
        threshold = abs(first) * 0.05
        if change > threshold:
            trend = "상승 추세"
        elif change < -threshold:
            trend = "하락 추세"
    return {
        "period": f"{items[0]['date']} ~ {items[-1]['date']}",
        "count": len(items),
        "metrics": {
            "total": round(sum(values), 2),
            "average": round(fmean(values), 2),
            "max": max(values),
            "min": min(values),
            "standard_deviation": round(pstdev(values), 2),
        },
        "trend": trend,
    }
