import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Location API")

# 저장 파일: 실행 위치와 무관하게 항상 backend/data/records.jsonl
DATA_DIR = Path(__file__).parent / "data"
RECORDS_FILE = DATA_DIR / "records.jsonl"
KST = timezone(timedelta(hours=9))

LOCATIONS = {
    "강남": {"lat": 37.4979, "lon": 127.0276},
    "여의도": {"lat": 37.5219, "lon": 126.9245},
    "마포": {"lat": 37.5663, "lon": 126.9014},
    "울산": {"lat": 35.5384, "lon": 129.3114},
    "광주": {"lat": 35.1595, "lon": 126.8526},
    "충청": {"lat": 36.6357, "lon": 127.4917},
    "강릉": {"lat": 37.7519, "lon": 128.8761},
    "제주": {"lat": 33.4996, "lon": 126.5312},
}


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/locations")
def get_locations():
    return LOCATIONS


@app.get("/locations/{name}")
def get_location(name: str):
    if name not in LOCATIONS:
        raise HTTPException(status_code=404, detail="location not found")
    return LOCATIONS[name]


# ── 방문 기록 ──────────────────────────────────────────────────
class RecordIn(BaseModel):
    user_name: str = Field(min_length=1, max_length=20)
    region: str
    score: int = Field(ge=1, le=5)
    memo: str = Field(default="", max_length=100)


def _load_records() -> list[dict]:
    if not RECORDS_FILE.exists():
        return []
    records = []
    with RECORDS_FILE.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def _append_record(record: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with RECORDS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


@app.post("/records", status_code=201)
def create_record(body: RecordIn):
    if body.region not in LOCATIONS:
        raise HTTPException(status_code=400, detail="unknown region")

    center = LOCATIONS[body.region]
    # 좌표는 저장 시점에 한 번만 계산해 파일에 고정한다.
    record = {
        "id": uuid.uuid4().hex[:8],
        "user_name": body.user_name,
        "region": body.region,
        "score": body.score,
        "memo": body.memo,
        "lat": round(center["lat"] + random.uniform(-0.01, 0.01), 6),
        "lon": round(center["lon"] + random.uniform(-0.01, 0.01), 6),
        "created_at": datetime.now(KST).isoformat(),
    }
    _append_record(record)
    return record


@app.get("/records")
def list_records(
    region: str | None = None,
    min_score: int | None = None,
    keyword: str | None = None,
):
    records = _load_records()
    # 선택적 필터 (AND 조건). 모두 None이면 전체 반환
    if region is not None:
        records = [r for r in records if r["region"] == region]
    if min_score is not None:
        records = [r for r in records if r["score"] >= min_score]
    if keyword:
        kw = keyword.lower()
        records = [r for r in records if kw in r.get("memo", "").lower()]
    records.reverse()  # 파일은 시간순 append → 뒤집으면 최신이 앞
    return {"count": len(records), "records": records}


@app.get("/records/user/{user_name}")
def list_user_records(user_name: str):
    records = [r for r in _load_records() if r.get("user_name") == user_name]
    records.reverse()  # 최신순
    avg_score = round(sum(r["score"] for r in records) / len(records), 1) if records else 0
    return {
        "user_name": user_name,
        "count": len(records),
        "avg_score": avg_score,
        "records": records,
    }


@app.delete("/records/{record_id}")
def delete_record(record_id: str):
    records = _load_records()
    remaining = [r for r in records if r.get("id") != record_id]
    if len(remaining) == len(records):
        raise HTTPException(status_code=404, detail=f"record '{record_id}' not found")

    # 임시 파일에 먼저 쓰고 원본과 원자적으로 교체 → 중간 실패 시 원본 보존
    tmp_file = RECORDS_FILE.with_suffix(".jsonl.tmp")
    with tmp_file.open("w", encoding="utf-8") as f:
        for r in remaining:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp_file.replace(RECORDS_FILE)
    return {"deleted": record_id}


@app.get("/stats")
def get_stats():
    records = _load_records()
    if not records:
        return {"total": 0, "user_count": 0, "overall_avg": 0, "by_region": []}

    by_region: dict[str, list[int]] = {}
    for r in records:
        by_region.setdefault(r["region"], []).append(r["score"])

    region_stats = [
        {"region": region, "count": len(scores), "avg_score": round(sum(scores) / len(scores), 1)}
        for region, scores in by_region.items()
    ]
    region_stats.sort(key=lambda x: x["count"], reverse=True)

    return {
        "total": len(records),
        "user_count": len({r["user_name"] for r in records}),
        "overall_avg": round(sum(r["score"] for r in records) / len(records), 1),
        "by_region": region_stats,
    }
