from server.app.services.plan_scraper import PlanScraper
import geopandas as gpd
from pathlib import Path
import zipfile

# נתיב ל-ZIP
zip_path = Path("data/polygon.zip")
extract_path = Path("data/unzipped_polygon")

# חילוץ ה-ZIP
with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(extract_path)

# טעינת הפוליגון
shp_path = list(extract_path.glob("*.shp"))[0]
polygon_gdf = gpd.read_file(shp_path)

# הרצת הסקרייפר
scraper = PlanScraper(polygon_gdf)
scraper.run()
