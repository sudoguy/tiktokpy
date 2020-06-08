import asyncio
from pathlib import Path
from urllib.parse import urljoin

from loguru import logger
from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.page import Page, Response


class Client:
    def __init__(self):
        self.base_url = "https://www.tiktok.com/"

    async def init_browser(self):
        params = {
            "headless": False,
            "args": ["--no-sandbox", "--disable-setuid-sandbox"],
        }

        self.browser: Browser = await launch(**params)
        logger.debug(f"Browser launched. Options: {params}")
        self.page: Page = await self.browser.newPage()

    async def goto(self, url: str, page=None, *args, **kwargs) -> Response:
        if not page:
            page = self.page

        full_url = urljoin(self.base_url, url)

        return await page.goto(full_url, *args, **kwargs)

    async def trending(self):
        logger.debug('Request "Trending" page')

        async def catch_response(response, fut):
            if "/item_list" in response.url:
                logger.debug(await response.json())
                fut.set_result(await response.json())

        response = asyncio.get_event_loop().create_future()

        self.page.on("response", lambda res: asyncio.create_task(catch_response(res, response)))
        _ = await self.goto("/trending", options={"waitUntil": "networkidle0", "timeout": 0})
        logger.debug('Got response from "Trending" page')
        # wait trending response json from puppeteer
        response: dict = await response
        logger.debug("Got trending json response from Puppeteer")

        # htmls = await self.page.JJeval(
        #     selector=".video-feed-item",
        #     pageFunction="elements => elements.map((el) => el.innerHTML)",
        # )
        logger.info(f"Found {len(response['items'])} trending items")

        return response["items"]

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
