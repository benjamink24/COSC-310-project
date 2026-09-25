from fastapi import FastAPI
from app.api.routes.restaurant_endpoints import router as restaurant_router

app = FastAPI()

app.include_router(restaurant_router)
#cd into app 
# terminal comand to start hosting on port 8000:
# uvicorn main:app --reload --host 127.0.0.1 --port 8000


@app.get("/health")
def health():
    return {"status": "ok"}