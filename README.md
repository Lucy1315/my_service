# 📍 우리 지역 체크인

방문한 지역과 만족도를 기록하고, 내 기록과 전체 현황을 한눈에 확인하는 서비스이다.
FastAPI(Application Programming Interface, API) 백엔드와 Streamlit 프론트엔드로 구성되며, 기록은 데이터베이스 없이 JSONL(JSON Lines) 파일에 저장한다.

## 구성

```
my_service/
├── backend/
│   ├── main.py            # FastAPI 서버 (포트 8000)
│   ├── data/records.jsonl # 방문 기록 저장 파일 (자동 생성, git 제외)
│   └── run.sh
├── frontend/
│   ├── app.py             # Streamlit 화면 (포트 8501)
│   └── run.sh
└── docker-compose.yml
```

## 실행

```bash
# 환경 (최초 1회)
conda create -n checkin python=3.11 -y
conda activate checkin
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt

# 백엔드 (터미널 1)
cd backend
uvicorn main:app --reload --port 8000      # http://localhost:8000/docs

# 프론트엔드 (터미널 2)
cd frontend
streamlit run app.py                        # http://localhost:8501
```

Docker로 실행하려면 `docker compose up --build` 한 줄이면 된다.
프론트엔드는 환경변수 `BACKEND_URL`(기본값 `http://localhost:8000`)로 백엔드 주소를 찾는다.

## 화면 구성

| 탭 | 기능 |
|---|---|
| 기록 남기기 | 이름·지역·만족도(1~5)·한 줄 메모를 입력해 저장한다 |
| 내 기록 | 이름으로 조회해 기록 수·평균 만족도·기록 표를 보고, 잘못 남긴 기록을 삭제한다 |
| 전체 현황 | 총 기록 수·참여자 수·전체 평균, 지역별 평균 만족도 그래프, 전체 기록 표, CSV 내려받기 |
| 사이드바 | 지역·최소 만족도·메모 키워드로 전체 기록 표와 CSV를 필터링한다 (모든 탭에서 보임) |

"전체 현황" 탭 맨 아래의 랜덤 지도는 실습 시작 코드의 데모이며 저장된 기록과 무관하다.

## API

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/locations` | 8개 지역의 위경도 |
| GET | `/locations/{name}` | 지역 1개의 위경도 (없으면 404) |
| POST | `/records` | 기록 저장 → 201, 저장된 기록 1건 응답 |
| GET | `/records` | 전체 기록 `{"count", "records"}` 최신순. 쿼리 `region`·`min_score`·`keyword`(AND) |
| GET | `/records/user/{user_name}` | 사용자별 기록 `{"user_name", "count", "avg_score", "records"}` (없어도 200) |
| DELETE | `/records/{record_id}` | 기록 삭제 → `{"deleted": id}` (없으면 404) |
| GET | `/records/export.csv` | `/records`와 같은 필터를 적용한 CSV (UTF-8 BOM, 엑셀 호환) |
| GET | `/stats` | `{"total", "user_count", "overall_avg", "by_region"}` |

### 기록 형식

요청 본문은 `user_name`(1~20자)·`region`(8개 지역 중 하나)·`score`(1~5)·`memo`(0~100자, 기본 "")이며, 서버가 `id`·`lat`·`lon`·`created_at`(KST)을 붙여 한 줄씩 저장한다.

```json
{"id":"a3f1c2d9","user_name":"김기획","region":"강남","score":4,"memo":"점심 맛집 많음","lat":37.5011,"lon":127.0243,"created_at":"2026-08-01T13:42:11+09:00"}
```

좌표는 저장 시점에 한 번만 계산해 고정하고, 삭제는 임시 파일에 쓴 뒤 원본과 교체해 중간 실패 시에도 원본을 보존한다.

## 개발 이력

| 단계 | 내용 |
|---|---|
| 1 | 방문 기록 입력 폼 (`st.form`) |
| 2 | 기록 저장 API + JSONL 파일 저장 |
| 3·4 | 폼–API 연동, 사용자 이름별 조회 |
| 5 | 지역별 통계 API와 대시보드 |
| 6 | 기록 삭제 (원자적 파일 교체) |
| 7 | 지역·만족도·키워드 검색 필터 |
| 8 | CSV 내보내기 (utf-8-sig) |
| 9 | 탭 기반 화면 정리 |
