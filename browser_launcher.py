from playwright.async_api import async_playwright

DEFAULT_BROWSER_ARGS = [
    "--disable-dev-shm-usage",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-gpu",
    "--disable-extensions",
    "--disable-background-networking",
    "--disable-background-timer-throttling",
    "--disable-client-side-phishing-detection",
    "--disable-default-apps",
    "--disable-sync",
    "--disable-translate",
    "--mute-audio",
]


class BrowserLauncher:
    """Async context manager for Playwright Chromium browser lifecycle."""

    def __init__(self, headless: bool = True, args: list[str] | None = None):
        self.headless = headless
        self.args = args or DEFAULT_BROWSER_ARGS
        self._playwright = None
        self.browser = None

    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        self.browser = await self._playwright.chromium.launch(
            headless=self.headless,
            args=self.args,
            chromium_sandbox=False,
        )
        return self.browser

    async def __aexit__(self, exc_type, exc, tb):
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()
