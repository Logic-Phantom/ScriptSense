from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from review import router as review_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(review_router, prefix="/api/review")