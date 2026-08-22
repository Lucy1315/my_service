from fastapi import FastAPI, HTTPException

app = FastAPI(title="Location API")

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
