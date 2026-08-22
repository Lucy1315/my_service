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
        st.success(f"이름: {name} · 지역: {region} · 만족도: {rating} · 메모: {memo}")

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
