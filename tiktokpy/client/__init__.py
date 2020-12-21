import asyncio
import json
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlencode, urljoin

from dynaconf import settings
from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.page import Page, Response
from pyppeteer_stealth import (
    iframe_content_window,
    media_codecs,
    navigator_permissions,
    navigator_plugins,
    navigator_webdriver,
    webgl_vendor,
    window_outerdimensions,
)

from tiktokpy.utils.client import block_resources_and_sentry
from tiktokpy.utils.logger import logger


class Client:
    def __init__(self):
        self.base_url = settings.BASE_URL

        self.cookies = json.loads(settings.get("COOKIES", "[]"))

    async def init_browser(self, headless: bool):
        params = {
            "headless": headless,
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",
            ],
        }

        self.browser: Browser = await launch(**params)
        logger.debug(f"🎉 Browser launched. Options: {params}")

    async def stealth(self, page: Page):
        await iframe_content_window(page)
        await media_codecs(page)
        await navigator_permissions(page)
        await navigator_plugins(page)
        await navigator_webdriver(page)
        await webgl_vendor(page)
        await window_outerdimensions(page)

    async def new_page(self, blocked_resources: Optional[List[str]] = None) -> Page:
        page: Page = await self.browser.newPage()

        # set stealth mode for tiktok
        await self.stealth(page)

        await page.setCookie(*self.cookies)

        if blocked_resources is not None:
            await page.setRequestInterception(True)
            page.on(
                "request",
                lambda req: asyncio.create_task(
                    block_resources_and_sentry(req, blocked_resources),
                ),
            )

        return page

    async def goto(
        self,
        url: str,
        page: Page,
        query_params: Optional[dict] = None,
        *args,
        **kwargs,
    ) -> Response:
        full_url = urljoin(self.base_url, url)

        if query_params:
            query_params_ = urlencode(query=query_params)
            full_url = f"{full_url}?{query_params_}"

        return await page.goto(full_url, *args, **kwargs)

    async def screenshot(self, path: str, page: Page):
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        await page.screenshot({"path": path})

    @classmethod
    async def create(cls, headless: bool = True):
        self = Client()
        await self.init_browser(headless=headless)

        return self
