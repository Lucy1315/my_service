#!/bin/bash
# 프론트엔드 실행:  ./run.sh   →  http://localhost:8501
# (백엔드를 먼저 켜둘 것)

cd "$(dirname "$0")"

# 맥에서 라이브러리 중복 로드 에러(OMP: Error #15) 날 때 필요
export KMP_DUPLICATE_LIB_OK=TRUE

export BACKEND_URL=http://localhost:8000

streamlit run app.py --server.port 8501
