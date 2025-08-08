from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from review import router as review_router
from js_analyzer import router as js_analyzer_router
from enhanced_js_analyzer import router as enhanced_js_analyzer_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(review_router, prefix="/api/review")
app.include_router(js_analyzer_router, prefix="/api/js")
app.include_router(enhanced_js_analyzer_router, prefix="/api/enhanced-js")