import os
import random

import pandas as pd
import requests
import streamlit as st

BACKEND_URL = os.environ.get("BACKEND_URL", "ttp://localhost:git")

st.set_page_config(page_title="위치 랜덤 데이터 시각화", layout="wide")
st.title("위치 기반 랜덤 데이터 시각화")

try:
    locations = requests.get(f"{BACKEND_URL}/locations", timeout=5).json()
except requests.exceptions.RequestException as e:
    st.error(f"백엔드 연결 실패: {e}")
    st.stop()

# ── 방문 기록 입력 폼 ──────────────────────────────────────────
st.subheader("방문 기록 입력")
with st.form("record_form"):
    name = st.text_input("이름")
    region = st.selectbox("지역", list(locations.keys()))
    rating = st.slider("만족도", 1, 5, 3)
    memo = st.text_input("한 줄 메모")
    submitted = st.form_submit_button("기록 저장")

if submitted:
    if not name.strip():
        st.warning("이름을 입력해주세요")
    else:
        try:
            res = requests.post(
                f"{BACKEND_URL}/records",
                json={"user_name": name.strip(), "region": region, "score": rating, "memo": memo},
                timeout=5,
            )
        except requests.exceptions.RequestException as e:
            st.error(f"저장 실패(백엔드 연결): {e}")
        else:
            if res.status_code == 201:
                saved = res.json()
                st.success(
                    f"저장 완료 · 이름: {saved['user_name']} · 지역: {saved['region']} "
                    f"· 만족도: {saved['score']} · 메모: {saved['memo']}"
                )
            else:
                st.error(f"저장 실패({res.status_code}): {res.text}")

# ── 내 기록 조회 ──────────────────────────────────────────────
st.subheader("내 기록 조회")
query_name = st.text_input("조회할 이름")
if st.button("내 기록 보기"):
    if not query_name.strip():
        st.warning("조회할 이름을 입력해주세요")
    else:
        try:
            result = requests.get(
                f"{BACKEND_URL}/records/user/{query_name.strip()}", timeout=5
            ).json()
        except requests.exceptions.RequestException as e:
            st.error(f"조회 실패(백엔드 연결): {e}")
        else:
            if result["count"] == 0:
                st.info(f"'{query_name.strip()}' 이름으로 남긴 기록이 없습니다.")
            else:
                m1, m2 = st.columns(2)
                m1.metric("내 기록 수", result["count"])
                m2.metric("평균 만족도", result["avg_score"])
                st.dataframe(pd.DataFrame(result["records"]))

# ── 전체 기록 ─────────────────────────────────────────────────
st.subheader("전체 기록")
try:
    all_records = requests.get(f"{BACKEND_URL}/records", timeout=5).json()
except requests.exceptions.RequestException as e:
    st.error(f"기록 조회 실패: {e}")
else:
    st.caption(f"총 {all_records['count']}건 (최신순)")
    if all_records["count"]:
        st.dataframe(pd.DataFrame(all_records["records"]))
    else:
        st.info("아직 저장된 기록이 없습니다.")

city = st.selectbox("지역 선택", list(locations.keys()))
n_points = st.slider("랜덤 포인트 개수", 10, 200, 50)

center = locations[city]

random.seed()
df = pd.DataFrame(
    {
        "lat": [center["lat"] + random.uniform(-0.02, 0.02) for _ in range(n_points)],
        "lon": [center["lon"] + random.uniform(-0.02, 0.02) for _ in range(n_points)],
        "value": [random.randint(1, 100) for _ in range(n_points)],
    }
)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"{city} 지도")
    st.map(df, latitude="lat", longitude="lon", size="value")

with col2:
    st.subheader("값 분포")
    st.bar_chart(df["value"])

st.subheader("원본 데이터")
st.dataframe(df)
