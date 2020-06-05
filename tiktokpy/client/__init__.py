from pathlib import Path

from loguru import logger
from pyppeteer import launch


class Client:
    async def init_browser(self):
        params = {
            "headless": True,
        }

        self.browser = await launch(**params)
        logger.debug(f"Browser launched. Options: {params}")
        self.page = await self.browser.newPage()

    async def goto(self, url: str, page=None, *args, **kwargs):
        if not page:
            page = self.page

        return await page.goto(url, *args, **kwargs)

    async def trending(self):
        logger.debug('Request "Trending" page')
        _trending = await self.goto("https://www.tiktok.com/trending")

        logger.debug("Start waiting .video-feed-item")
        await self.page.waitForSelector(".video-feed-item")
        logger.debug("End waiting .video-feed-item")

        return _trending

    async def screenshot(self, path: str, page=None):
        if not page:
            page = self.page

        Path(path).parent.mkdir(parents=True, exist_ok=True)

        await page.screenshot({"path": path})

    @classmethod
    async def create(cls):
        self = Client()
        await self.init_browser()

        return self
