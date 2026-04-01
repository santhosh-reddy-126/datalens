from browser_launcher import BrowserLauncher
import asyncio
import re
from pydantic import BaseModel
from settings import settings

class ProductRequest(BaseModel):
    url: str


def extract_product_id(url: str):
    match = re.search(r"/(?:dp|gp/product|d)/([A-Z0-9]{10})", url)
    return match.group(1) if match else None

async def scrape_page(context, url):
    async with context.new_page() as page:
        try:
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
        async with browser.new_context() as context:
            tasks = [scrape_page(context, url) for url in urls]
            results = await asyncio.gather(*tasks)
            return results


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






