#!/bin/bash
# 백엔드 실행:  ./run.sh   →  http://localhost:8000/docs

cd "$(dirname "$0")"

# 맥에서 라이브러리 중복 로드 에러(OMP: Error #15) 날 때 필요
export KMP_DUPLICATE_LIB_OK=TRUE

uvicorn main:app --reload --port 8000
