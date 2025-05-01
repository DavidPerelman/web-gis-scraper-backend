import pycurl
import json
from io import BytesIO
import geopandas as gpd
from shapely import Polygon
from shapely.geometry import shape


class IplanFetcher:
    def __init__(self, polygon_gdf: gpd.GeoDataFrame):
        self.polygon = polygon_gdf
        self.bbox = self.polygon.total_bounds  # [minx, miny, maxx, maxy]
        self.plans = []

    def fetch_plans_by_bbox(self) -> dict:
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

        try:
            return json.loads(response_body)
        except json.JSONDecodeError:
            raise Exception("❌ Server did not return valid JSON")

    def filter_plans_in_polygon(self, raw_json: dict) -> gpd.GeoDataFrame:
        features = raw_json.get("features", [])
        if not features:
            return gpd.GeoDataFrame()

        records = []
        for f in features:
            geom = f.get("geometry")
            attrs = f.get("attributes", {})

            if geom is None or "rings" not in geom:
                continue  # דלג על תכונה בעייתית

            try:
                polygon = Polygon(geom["rings"][0])  # לפעמים יש יותר מ־1
                records.append({**attrs, "geometry": polygon})
            except Exception as e:
                print("⚠️ Failed to create polygon:", e)
                continue

        if not records:
            return gpd.GeoDataFrame()

        gdf = gpd.GeoDataFrame(records)
        gdf.set_geometry("geometry", inplace=True)
        gdf.set_crs(epsg=2039, inplace=True)

        filtered = gdf[gdf.intersects(self.polygon.unary_union)]
        return filtered

    def run(self):
        raw = self.fetch_plans_by_bbox()
        filtered = self.filter_plans_in_polygon(raw)
        return filtered
