import pycurl
import json
import time
import os
from io import BytesIO
import geopandas as gpd
from shapely.geometry import Polygon
from bs4 import BeautifulSoup
from splinter import Browser
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv
from geojson import Feature, FeatureCollection

load_dotenv()
CHROMEDRIVER_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", os.getenv("CHROMEDRIVER_PATH")
)
CHROMEDRIVER_PATH = os.path.abspath(CHROMEDRIVER_PATH)


class IplanFetcher:
    def __init__(self, polygon_gdf: gpd.GeoDataFrame):
        self.polygon = polygon_gdf
        self.bbox = self.polygon.total_bounds
        self.plans = []

        self.key_mapping = {
            'מגורים (יח"ד)': "residence_units",
            'מגורים (מ"ר)': "residence_sqm",
            'מסחר (מ"ר)': "commerce_sqm",
            'תעסוקה (מ"ר)': "employment_sqm",
            'מבני ציבור (מ"ר)': "public_buildings_sqm",
            "חדרי מלון / תיירות (חדר)": "hotel_rooms_count",
            'חדרי מלון / תיירות (מ"ר)': "hotel_rooms_sqm",
            'דירות קטנות (יח"ד)': "small_apartments_units",
            'דירות להשכרה (יח"ד)': "rental_units",
        }

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
        c.setopt(c.TIMEOUT, 20)
        c.setopt(c.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_1)
        c.setopt(
            c.HTTPHEADER,
            [
                "Accept: application/json",
                "Content-Type: application/x-www-form-urlencoded",
            ],
        )
        c.perform()
        c.close()

        response_body = buffer.getvalue().decode("utf-8")
        return json.loads(response_body)

    def filter_plans_in_polygon(self, raw_json: dict) -> list[dict]:
        features = raw_json.get("features", [])
        filtered = []

        for plan in features:
            geom_data = plan.get("geometry", {})
            rings = geom_data.get("rings")
            if not rings:
                continue
            polygon = Polygon(shell=rings[0], holes=rings[1:])
            if self.polygon.unary_union.contains(polygon.centroid):
                filtered.append(plan)
        return filtered

    def extract_quantitative_data(self, plan: dict) -> dict:
        url = plan["attributes"].get("pl_url")
        if not url:
            return plan

        service = Service(executable_path=CHROMEDRIVER_PATH)

        if not os.path.isfile(CHROMEDRIVER_PATH):
            raise FileNotFoundError(
                f"❌ chromedriver not found at: {CHROMEDRIVER_PATH}"
            )

        browser = Browser("chrome", headless=True, service=service)
        browser.visit(url)
        time.sleep(7)

        try:
            for b in browser.find_by_tag("button"):
                if b.text == "נתונים נוספים":
                    b.click()

            soup = BeautifulSoup(browser.html, "html.parser")
            li_tags = soup.find_all(
                "li", class_="sv4-icon-arrow uk-open uk-hide-arrow ng-star-inserted"
            )
            obj = {}
            for li in li_tags:
                divs = li.find_all(
                    "div", class_="uk-accordion-content uk-margin-remove"
                )
                for div in divs:
                    uls = div.find_all("ul")
                    for ul in uls:
                        for li_inner in ul.find_all("li"):
                            key_el = li_inner.find(
                                "div", class_="uk-width-expand ng-star-inserted"
                            )
                            val_el = li_inner.find("b")
                            if key_el and val_el:
                                obj[key_el.text.strip()] = val_el.text.strip()

            plan["attributes"].update(obj)
        finally:
            browser.quit()
        return plan

    def normalize_keys(self, plan: dict) -> dict:
        original = plan["attributes"]
        normalized = {}
        for k, v in original.items():
            new_key = self.key_mapping.get(k, k)
            normalized[new_key] = v
        plan["attributes"] = normalized
        return plan

    def build_geodataframe_feature_collection(
        self, plans: list[dict]
    ) -> gpd.GeoDataFrame:
        features = []

        for plan in plans:
            rings = plan.get("geometry", {}).get("rings", [])
            if not rings:
                continue
            exterior = rings[0]
            holes = rings[1:]

            try:
                polygon = Polygon(shell=exterior, holes=holes)
                feature = Feature(geometry=polygon, properties=plan["attributes"])
                features.append(feature)
            except Exception as e:
                print(
                    f"⚠️ Failed to build polygon for {plan['attributes'].get('pl_number')}: {e}"
                )
                continue

        collection = FeatureCollection(features)
        gdf = gpd.GeoDataFrame.from_features(collection, crs="EPSG:2039")
        return gdf

    def run(self) -> list[dict]:
        raw = self.fetch_plans_by_bbox()
        filtered = self.filter_plans_in_polygon(raw)

        # 🧪 נריץ רק על 2 ראשונות לבדיקה
        filtered_subset = filtered[:2]

        enriched = []
        for plan in filtered_subset:
            plan = self.extract_quantitative_data(plan)
            plan = self.normalize_keys(plan)
            enriched.append(plan)

        geodataframe = self.build_geodataframe_feature_collection(enriched)

        print(f"✅ Filtered + enriched plans: {len(enriched)}")
        return geodataframe
