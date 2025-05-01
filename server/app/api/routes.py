from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import geopandas as gpd
from pathlib import Path

from app.services.iplan_fetcher import IplanFetcher

router = APIRouter()


@router.post("/upload-polygon")
async def upload_polygon(file: UploadFile = File(...)):
    allowed_extensions = (".zip", ".geojson", ".json", ".shp")
    if not file.filename.endswith(allowed_extensions):
        raise HTTPException(status_code=400, detail="Invalid file format")

    upload_path = Path("temp_uploads")
    upload_path.mkdir(parents=True, exist_ok=True)

    file_location = upload_path / file.filename

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        if file.filename.endswith(".zip"):
            # חילוץ ה־ZIP לתוך תיקייה
            extract_dir = upload_path / file.filename.replace(".zip", "")
            extract_dir.mkdir(parents=True, exist_ok=True)
            shutil.unpack_archive(str(file_location), str(extract_dir))

            # חיפוש קובץ SHP
            shp_files = list(extract_dir.glob("*.shp"))
            if not shp_files:
                raise Exception("No .shp file found inside the ZIP archive.")

            gdf = gpd.read_file(shp_files[0])

        else:
            gdf = gpd.read_file(file_location)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {e}")

    scraper = IplanFetcher(gdf)
    plans_data = scraper.run()

    return {
        "message": "Polygon uploaded and plans fetched successfully",
        "features_uploaded": len(gdf),
        "plans_fetched": len(plans_data.get("features", [])),
        "plans": plans_data.get("features", [])[:5],  # נשלח רק חלק קטן לצורך הדגמה
    }
