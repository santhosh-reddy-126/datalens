from browser_launcher import BrowserLauncher
import asyncio
import re
import requests
from pydantic import BaseModel
from settings import settings



class ProductRequest(BaseModel):
    url: str


def extract_product_id(url:str):
    match = re.search(r"/dp/([A-Z0-9]{10})",url,re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None



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
    async with context:
        try:
            page = await context.new_page()
            await page.goto(url, timeout=settings.playwright_timeout_ms)
            await page.wait_for_selector("span#productTitle", timeout=10000)
            title = (await page.locator("span#productTitle").first.inner_text()).strip()
            price_locator = page.locator("#corePrice_feature_div span.a-offscreen")
            price = await price_locator.first.inner_text() if await price_locator.count() > 0 else None
            rating_locator = page.locator("#averageCustomerReviews_feature_div #acrPopover")
            rating = await rating_locator.first.get_attribute("title") if await rating_locator.count() > 0 else None
            image_locator = page.locator("#landingImage")
            image_url = await image_locator.get_attribute("src") if await image_locator.count() > 0 else None
            return {
                "url": url,
                "title": title,
                "price": price,
                "rating": rating,
                "image_url": image_url
            }
        except Exception:
            return {"url": url, "error": True}

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






