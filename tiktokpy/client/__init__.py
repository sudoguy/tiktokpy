import asyncio
from pathlib import Path
from typing import List
from urllib.parse import urljoin

from loguru import logger
from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.page import Page, Response
from tqdm import tqdm

from tiktokpy.utils.client import block_resources, catch_response_and_store


class Client:
    def __init__(self):
        self.base_url = "https://www.tiktok.com/"

    async def init_browser(self):
        params = {
            "headless": True,
            "args": ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
        }

        self.browser: Browser = await launch(**params)
        logger.debug(f"🎉Browser launched. Options: {params}")
        self.page: Page = await self.browser.newPage()

        await self.page.setRequestInterception(True)
        self.page.on(
            "request",
            lambda req: asyncio.create_task(block_resources(req, ["resources", "image"])),
        )

    async def goto(self, url: str, page=None, *args, **kwargs) -> Response:
        if not page:
            page = self.page

        full_url = urljoin(self.base_url, url)

        return await page.goto(full_url, *args, **kwargs)

    async def trending(self, amount: int):
        logger.debug('📨Request "Trending" page')

        result: List[dict] = []

        pbar = tqdm(total=amount, desc="📈Getting trending")

        self.page.on(
            "response", lambda res: asyncio.create_task(catch_response_and_store(res, result)),
        )
        _ = await self.goto("/trending", options={"waitUntil": "networkidle0", "timeout": 0})
        logger.debug('📭Got response from "Trending" page')

        while len(result) < amount:

            logger.debug("🖱Trying to scroll to last video item")
            await self.page.evaluate(
                """
                document.querySelector('.video-feed-item:last-child')
                    .scrollIntoView();
            """,
            )

            elements = await self.page.JJ(".video-feed-item")
            logger.debug(f"🔎Found {len(elements)} items for clear")

            pbar.n = min(len(result), amount)
            pbar.update()

            if len(elements) < 150:
                logger.debug("🔻Too less for clearing page")
                continue

            await self.page.JJeval(
                ".video-feed-item:not(:last-child)",
                pageFunction="(elements) => elements.forEach(el => el.remove())",
            )
            logger.debug(f"🎉Cleaned {len(elements) - 1} items from page")

        return result[:amount]

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
