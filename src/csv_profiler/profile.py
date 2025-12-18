from __future__ import annotations

from pathlib import Path
from statistics import mean
from collections import Counter

def basic_profile(rows: list[dict[str, str]], source: Path) -> dict:
    source = Path(source)
    
    if not rows:
        return {"summary": {"rows": 0, "columns": 0}, "columns": {}}
    
    columns = list(rows[0].keys())
    report_columns = {}
    
    for col in columns:
        col_values = column_values(rows, col)
        col_type = infer_type(col_values)
        
        missing_count = 0
        for v in col_values:
            if is_missing(v):
                missing_count = missing_count + 1
        
        usable = []
        for v in col_values:
            if not is_missing(v):
                usable.append(v)
        
        unique_count = len(set(usable))
        
        report_columns[col] = {
            "type": col_type,
            "missing": missing_count,
            "unique": unique_count
        }
        
        if col_type == "number":
            stats = numeric_stats(col_values)
            if stats:
                report_columns[col]["min"] = stats["min"]
                report_columns[col]["max"] = stats["max"]
                report_columns[col]["mean"] = stats["mean"]
                report_columns[col]["count"] = stats["count"]
        
        if col_type == "text":
            text_data = text_stats(col_values, 5)
            if text_data:
                report_columns[col]["top"] = text_data.get("top", [])
    
    return {
        "summary": {
            "rows": len(rows),
            "columns": len(columns)
        },
        "columns": report_columns
    }


def is_missing(value: str | None) ->bool:
    if value is None:
        return True
    cleaned = value.strip().casefold()
    return cleaned in {"","na","n/a","null","none","nan"}

def try_float(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None
    
def infer_type(values:list[str]) -> str:
    usable = [v for v in values if not is_missing(v)]
    if not usable:
        return"text"
    for v in usable:
        if try_float(v) is None:
            return"text"
    return"number"

def column_values(rows: list[dict[str, str]], col: str) -> list[str]:
    R_list = []
    for row in rows:
        R_list.append(row.get(col, ""))
    return R_list


def numeric_stats(values: list[str]) -> dict:
    if values is None:
        return None
    
    usable = []
    for v in values:
        if not is_missing(v):
            usable.append(v)
    
    nums = []
    for v in usable:
        num = try_float(v)
        if num is not None:
            nums.append(num)
    
    if not nums:
        return None
    
    unique = len(set(nums))
    missing = len(values) - len(nums)
    
    return {
        "min": min(nums),
        "max": max(nums),
        "count": len(nums),
        "mean": mean(nums),
        "unique": unique,
        "missing": missing
    }


def text_stats(values: list[str], top_k: int = 5) -> dict:
    usable = []
    for v in values:
        if not is_missing(v) and try_float(v) is None:
            usable.append(v)
    
    count_dict = {}
    for v in usable:
        count_dict[v] = count_dict.get(v, 0) + 1
    
    top = sorted(count_dict.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
    unique = len(set(count_dict))
    missing = len(values) - len(usable)
    
    return {
        "top": top,
        "unique": unique,
        "missing": missing
    }

def profile_rows(rows:list[dict[str, str]]) -> dict:
    n_rows, columns = len(rows),list(rows[0].keys())
    col_profiles = []
    for col in columns:
        values = [r.get(col,"") for r in rows]
        usable = [v for v in values if not is_missing(v)]
        missing = len(values) - len(usable)
        inferred = infer_type(values)
        unique = len(set(usable))
        profile ={
            "name":col,
            "type":inferred,
            "missing":missing,
            "missing_pct": 100.0 * missing / n_rows if n_rows else 0.0,
            "unique": unique,
        }
        if inferred =="number":
            nums = [try_float(v) for v in usable]
            nums = [x for x in nums if x is not None]
            if nums:
                profile.update({"min":min(nums),"max":max(nums),"mean": sum(nums)/len(nums)})
        col_profiles.append(profile)
    return {"n_rows":n_rows,"n_cols":len(columns),"columns":col_profiles}