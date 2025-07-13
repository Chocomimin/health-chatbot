# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chat_routes import router as chat_router  # importing routes
from auth import router as auth_router
app = FastAPI()

# ✅ CORS Setup (for frontend communication)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://health-chatbot-liard.vercel.app/"],  # <-- Replace with your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include chat routes
app.include_router(chat_router)
app.include_router(auth_router)
