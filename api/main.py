from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import snapshots, tournament, admin, predictions, upsets

app = FastAPI(title="World Cup 2026 Simulator API", version="1.0.0")

# Autoriser les requêtes CORS depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistrement des routeurs
app.include_router(snapshots.router, prefix="/api/snapshots", tags=["snapshots"])
app.include_router(tournament.router, prefix="/api/tournament", tags=["tournament"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
app.include_router(upsets.router, prefix="/api/upsets", tags=["upsets"])

@app.get("/")
def read_root():
    return {"message": "Welcome to World Cup 2026 Simulator API"}
