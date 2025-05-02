from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import geopandas as gpd
from pathlib import Path

from shapely import Polygon
from app.services.iplan_fetcher import IplanFetcher
from shapely.geometry import mapping

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
            extract_dir = upload_path / file.filename.replace(".zip", "")
            extract_dir.mkdir(parents=True, exist_ok=True)
            shutil.unpack_archive(str(file_location), str(extract_dir))
            shp_files = list(extract_dir.glob("*.shp"))
            if not shp_files:
                raise Exception("No .shp file found inside the ZIP archive.")
            gdf = gpd.read_file(shp_files[0])
        else:
            gdf = gpd.read_file(file_location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {e}")

    # העשרת תכניות
    fetcher = IplanFetcher(gdf)
    plans = fetcher.run()

    print(type(plans), plans)

    # # המרה של כל תוכנית לאובייקט נקי מ־Polygon
    cleaned = []
    # for plan in plans:
    #     cleaned_plan = {
    #         "attributes": plan["attributes"],
    #         "geometry": mapping(
    #             Polygon(plan["geometry"]["rings"][0])
    #         ),  # רק הטבעת החיצונית
    #     }
    #     cleaned.append(cleaned_plan)

    return {
        "message": "Plans fetched and enriched successfully",
        "count": len(cleaned),
        "plans": cleaned,
    }
