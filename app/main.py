from fastapi import FastAPI
from app.api.routes import router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="GIS Scraper API",
    description="API לקבלת פוליגון, ביצוע גרידת נתונים והחזרת שכבת תוצאה",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://web-gis-scraper.vercel.app",
    ],  # או ["*"] רק זמנית בזמן פיתוח
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@router.get("/")
async def main():
    return {"message": "Wellcome to web-gis-scraper api!"}


app.include_router(router)
