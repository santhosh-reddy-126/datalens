from browser_launcher import BrowserLauncher
import asyncio
import re
import requests
from settings import settings
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from database.db import products_col, products_history_col




def extract_product_id(url:str):
    match = re.search(r"/dp/([A-Z0-9]{10})",url,re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None

async def get_latest_history(product_id: str):
    doc = products_history_col.find_one({"product_id": product_id}, sort=[("created_at", -1)])
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc



def get_clean_amazon_url(input_url: str):
    if not input_url:
        return None

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    if "amzn.in" in input_url or "a.co" in input_url:
        try:
            response = requests.get(
                input_url, 
                headers=headers, 
                allow_redirects=True, 
                timeout=15, 
                stream=True
            )
            final_url = response.url
            response.close() 
        except Exception:
            return None
    else:
        final_url = input_url

    asin_match = re.search(r"/(?:dp|gp/product|d)/([A-Z0-9]{10})", final_url, re.IGNORECASE)
        
    if asin_match:
        asin = asin_match.group(1).upper()
        return f"https://www.amazon.in/dp/{asin}"
        
    return None


async def scrape_page(context, url):
    page = None
    try:
        page = await context.new_page()

        await page.goto(
            url,
            timeout=settings.playwright_timeout_ms,
            wait_until="networkidle"  
        )

        final_url = page.url
        page_title = await page.title()

        try:
            await page.wait_for_selector("span#productTitle", timeout=15000)
            title_locator = page.locator("span#productTitle")
        except PlaywrightTimeoutError:
            title_locator = page.locator("#title span")

            if await title_locator.count() == 0:
                await page.screenshot(path="debug.png")  

                return {
                    "url": url,
                    "error": "Title not found",
                    "page_title": page_title,
                    "final_url": final_url
                }

        title = (await title_locator.first.inner_text()).strip()

        price = None
        price_locators = [
            "#corePrice_feature_div span.a-offscreen",
            "#priceblock_ourprice",
            "#priceblock_dealprice"
        ]

        for selector in price_locators:
            locator = page.locator(selector)
            if await locator.count() > 0:
                price = await locator.first.inner_text()
                break

        rating = None
        rating_locator = page.locator("#averageCustomerReviews_feature_div #acrPopover")
        if await rating_locator.count() > 0:
            rating = await rating_locator.first.get_attribute("title")

        image_url = None
        image_locator = page.locator("#landingImage")
        if await image_locator.count() > 0:
            image_url = await image_locator.first.get_attribute("src")

        return {
            "url": url,
            "title": title,
            "price": price,
            "rating": rating,
            "image_url": image_url,
            "final_url": final_url
        }

    except PlaywrightTimeoutError as e:
        return {
            "url": url,
            "error": "Page load timeout",
            "details": str(e)
        }

    except Exception as e:
        return {
            "url": url,
            "error": type(e).__name__,
            "details": str(e)
        }

    finally:
        if page:
            await page.close()


async def collect_multiple(urls):
    async with BrowserLauncher(headless=settings.playwright_headless) as browser:
        context = await browser.new_context()
        try:
            tasks = [scrape_page(context, url) for url in urls]
            results = await asyncio.gather(*tasks)
            return results
        finally:
            await context.close()


def clean_data(data):
    if not data:
        return None
    try:
        if data["price"]:
            data["price"] = float(re.sub(r"[^\d.]", "", data["price"]))
        else:
            data["price"] = None
        if data["rating"]:
            data["rating"] = float(data["rating"].split(" ")[0])
        else:
            data["rating"] = None
        return data
    except Exception as e:
        print("Cleaning error:", e)
        return None


