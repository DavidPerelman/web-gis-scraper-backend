from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="GIS Scraper API",
    description="API לקבלת פוליגון, ביצוע גרידת נתונים והחזרת שכבת תוצאה",
    version="0.1.0"
)

app.include_router(router)
