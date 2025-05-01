import requests
import geopandas as gpd


class PlanScraper:
    def __init__(self, polygon_gdf: gpd.GeoDataFrame):
        self.polygon = polygon_gdf
        self.bbox = self.polygon.total_bounds  # [minx, miny, maxx, maxy]
        self.session = requests.Session()
        self.plans = []

    def get_bbox_query(self) -> dict:
        minx, miny, maxx, maxy = self.bbox

        return {
            "geometryType": "esriGeometryEnvelope",
            "geometry": {
                "xmin": minx,
                "ymin": miny,
                "xmax": maxx,
                "ymax": maxy,
                "spatialReference": {"wkid": 2039},
            },
            "spatialRel": "esriSpatialRelIntersects",
            "returnGeometry": True,
            "outFields": "*",
            "f": "json",
        }

    def fetch_plans_by_bbox(self) -> dict:
        # שליחת בקשה וקבלת JSON
        pass

    def filter_plans_in_polygon(self, raw_json: dict) -> gpd.GeoDataFrame:
        # סינון התכניות לפי חיתוך גיאומטרי
        pass

    def run(self) -> gpd.GeoDataFrame:
        # שרשור כל התהליך
        pass
