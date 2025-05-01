import pycurl
import json
import geopandas as gpd
from io import BytesIO
from urllib.parse import urlencode


class PlanScraperPycurl:
    def __init__(self, polygon_gdf: gpd.GeoDataFrame):
        self.polygon = polygon_gdf
        self.bbox = self.polygon.total_bounds  # [minx, miny, maxx, maxy]
        self.plans = []

    def get_bbox_params(self) -> dict:
        minx, miny, maxx, maxy = self.bbox
        return {
            "f": "json",
            "geometryType": "esriGeometryEnvelope",
            "geometry": json.dumps(
                {
                    "xmin": minx,
                    "ymin": miny,
                    "xmax": maxx,
                    "ymax": maxy,
                    "spatialReference": {"wkid": 2039},
                }
            ),
            "spatialRel": "esriSpatialRelIntersects",
            "returnGeometry": "true",
            "outFields": "*",
            "orderByFields": "pl_number",
            "inSR": 2039,
            "outSR": 2039,
        }

    def fetch_plans_by_bbox(self) -> dict:
        url_base = "https://ags.iplan.gov.il/arcgisiplan/rest/services/PlanningPublic/Xplan/MapServer/1/query"
        full_url = f"{url_base}?{urlencode(self.get_bbox_params())}"

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, full_url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.USERAGENT, "Mozilla/5.0")
        c.setopt(c.TIMEOUT, 20)
        c.perform()
        status_code = c.getinfo(pycurl.RESPONSE_CODE)
        c.close()

        if status_code != 200:
            raise Exception(f"Request failed with status code {status_code}")

        body = buffer.getvalue().decode("utf-8")
        return json.loads(body)

    def run(self):
        return self.fetch_plans_by_bbox()
