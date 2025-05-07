import sys
import os
import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
from datetime import datetime

# הגדרת נתיב לדפדפן לפי מערכת ההפעלה
if sys.platform == "win32":
    CHROME_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe"
else:
    CHROME_PATH = "/usr/bin/chromium"

FAILED_PLANS_LOG_PATH = "missing_more_button_plans.txt"


async def extract_main_fields_async(plan: dict) -> dict:
    url = plan["attributes"].get("pl_url")
    if not url:
        return plan

    from pyppeteer import launch

    browser = await launch(
        headless=True,
        executablePath="/usr/bin/chromium",
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-accelerated-2d-canvas",
            "--no-first-run",
            "--no-zygote",
            "--single-process",
            "--disable-gpu",
        ],
    )

    page = await browser.newPage()
    await page.goto(url, {"waitUntil": "networkidle2"})
    await asyncio.sleep(8)  # חשוב לדף של מינהל התכנון

    try:
        # המתן לכפתור + גלול אליו
        await page.waitForSelector("#moreQuantitiesFocus", {"timeout": 8000})

        await page.evaluate(
            """
            () => {
                const el = document.querySelector("#moreQuantitiesFocus");
                if (el) {
                    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        """
        )
        await asyncio.sleep(7)

        # לחץ על הכפתור בתוך הדף עצמו
        await page.evaluate(
            """
            () => {
                const el = document.querySelector("#moreQuantitiesFocus");
                if (el) el.click();
            }
        """
        )

        # המתן לטעינה של הנתונים החדשים
        await asyncio.sleep(4)
        await page.waitForSelector("button.uk-accordion-title", {"timeout": 7000})

    except Exception as e:
        pl_number = plan["attributes"].get("pl_number")
        pl_url = plan["attributes"].get("pl_url")
        message = f"⚠️ No 'נתונים נוספים' button for plan: {pl_number} - {pl_url}"
        print(message)

        with open(FAILED_PLANS_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(message + "\n")

    html = await page.content()
    await browser.close()

    # 🛠 אופציונלי: שמירה לבדיקה ידנית
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"debug_plan_{ts}.html", "w", encoding="utf-8") as f:
        f.write(html)

    soup = BeautifulSoup(html, "html.parser")
    obj = {}

    # שליפת נתונים מהכפתורים המרכזיים
    accordion_buttons = soup.select("button.uk-accordion-title")
    for btn in accordion_buttons:
        key_el = btn.select_one("div.uk-width-expand")
        val_el = btn.select_one("div.uk-text-left b")

        if key_el and val_el:
            key = key_el.get_text(strip=True)
            val = val_el.get_text(strip=True)
            obj[key] = val

    print("🔍 Extracted quantitative data:", obj)
    plan["attributes"].update(obj)
    return plan
