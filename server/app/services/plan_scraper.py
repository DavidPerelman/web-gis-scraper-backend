import pycurl
import json
from io import BytesIO
import geopandas as gpd


class PlanScraper:
    def __init__(self, polygon_gdf: gpd.GeoDataFrame):
        self.polygon = polygon_gdf
        self.bbox = self.polygon.total_bounds  # [minx, miny, maxx, maxy]
        self.plans = []

    def fetch_plans(self) -> dict:
        minx, miny, maxx, maxy = self.bbox

        url = (
            "https://ags.iplan.gov.il/arcgisiplan/rest/services/PlanningPublic/Xplan/MapServer/1/query"
            "?f=json"
            "&where=pl_area_dunam%20%3C%3D15"
            "&returnGeometry=true"
            f"&geometry=%7B%22xmin%22%3A{minx}%2C%22ymin%22%3A{miny}%2C%22xmax%22%3A{maxx}%2C%22ymax%22%3A{maxy}%2C%22spatialReference%22%3A%7B%22wkid%22%3A2039%7D%7D"
            "&geometryType=esriGeometryEnvelope"
            "&inSR=2039"
            "&outFields=pl_number%2Cpl_name%2Cpl_url%2Cquantity_delta_120%2Cstation_desc%2Cplan_county_name"
            "&orderByFields=pl_number"
            "&outSR=2039"
        )

        print("🔗 Full URL:", url)

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.TIMEOUT, 20)  # מאפשר יותר זמן לשרת להגיב
        c.setopt(c.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_1)
        c.setopt(
            c.HTTPHEADER,
            [
                "Accept: application/json",
                "Content-Type: application/x-www-form-urlencoded",
            ],
        )

        try:
            c.perform()
            status_code = c.getinfo(pycurl.RESPONSE_CODE)
            if status_code != 200:
                raise Exception(f"Request failed with status code {status_code}")
        finally:
            c.close()

        response_body = buffer.getvalue().decode("utf-8")
        print("📦 Raw response body:")
        print(response_body[:500])

        # שמור את הגוף לקובץ לבדיקה אם יש בעיה
        with open("debug_response.html", "w", encoding="utf-8") as f:
            f.write(response_body)

        try:
            return json.loads(response_body)
        except json.JSONDecodeError:
            raise Exception("❌ Server did not return valid JSON")

    def filter_plans_in_polygon(self, raw_json: dict) -> gpd.GeoDataFrame:
        # future: implement geometry filtering
        pass

    def run(self):
        raw = self.fetch_plans()
        print("✅ Raw plans fetched:", raw)
        return raw
