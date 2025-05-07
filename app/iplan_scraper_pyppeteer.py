import sys
import os
import asyncio
from pyppeteer import launch
from pyppeteer.errors import TimeoutError
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

    html = ""
    obj = {}

    try:
        browser = await launch(
            headless=True,
            executablePath=CHROME_PATH,
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
        await page.goto(
            url,
            {
                "waitUntil": "networkidle2",
                "timeout": 60000,  # הגבלת זמן טעינה ל־60 שניות
            },
        )

        await asyncio.sleep(8)

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

            # לחץ על הכפתור
            await page.evaluate(
                """
                () => {
                    const el = document.querySelector("#moreQuantitiesFocus");
                    if (el) el.click();
                }
            """
            )

            await asyncio.sleep(4)
            await page.waitForSelector("button.uk-accordion-title", {"timeout": 7000})

        except Exception as e:
            pl_number = plan["attributes"].get("pl_number")
            pl_url = plan["attributes"].get("pl_url")
            message = f"⚠️ No 'נתונים נוספים' button for plan: {pl_number} - {pl_url}"
            print(message)
            plan["attributes"]["scrape_status"] = "no_button"

            with open(FAILED_PLANS_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(message + "\n")

        html = await page.content()

    except TimeoutError:
        print(f"❌ Timeout loading page: {url}")
        plan["attributes"]["scrape_status"] = "timeout"

    except Exception as e:
        print(f"❌ Unexpected error on {url}: {e}")
        plan["attributes"]["scrape_status"] = "error"

    finally:
        if "browser" in locals():
            await browser.close()

        # 🛠 שמור קובץ HTML לבדיקה גם אם היה כשל
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"debug_plan_{ts}.html", "w", encoding="utf-8") as f:
            f.write(html)

    if html:
        soup = BeautifulSoup(html, "html.parser")

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
