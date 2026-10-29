from fastapi import FastAPI
from app.api.routes.restaurant_endpoints import router as restaurant_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins= [
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "null",
    ],
    allow_credentials= False,
    allow_methods= ["*"],
    allow_headers= ["*"],
)



app.include_router(restaurant_router)



@app.get("/health")
def health():
    return {"status": "ok"}