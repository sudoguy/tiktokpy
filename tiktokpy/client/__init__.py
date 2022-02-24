import asyncio
import json
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlencode, urljoin

from dynaconf import settings
from playwright.async_api import Browser, Page, Playwright, PlaywrightContextManager, Response
from playwright_stealth import StealthConfig, stealth_async

from tiktokpy.utils.client import block_resources_and_sentry
from tiktokpy.utils.logger import logger


class Client:
    """Browser client"""

    def __init__(self):
        self.base_url = settings.BASE_URL
        self.playwright: Playwright

        self.cookies = json.loads(settings.get("COOKIES", "[]"))

    async def init_browser(self, headless: bool):
        self.playwright = await PlaywrightContextManager().start()

        params = {
            "headless": headless,
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",
                "--disable-notifications",
            ],
        }

        self.browser: Browser = await self.playwright.chromium.launch(**params)
        self.context = await self.browser.new_context()
        await self.context.add_cookies(self.cookies)
        logger.debug(f"🎉 Browser launched. Options: {params}")

    async def new_page(self, blocked_resources: Optional[List[str]] = None) -> Page:
        page: Page = await self.context.new_page()

        # set stealth mode for tiktok
        await stealth_async(
            page,
            StealthConfig(
                webdriver=True,
                webgl_vendor=True,
                chrome_app=False,
                chrome_csi=False,
                chrome_load_times=False,
                chrome_runtime=False,
                iframe_content_window=True,
                media_codecs=True,
                navigator_hardware_concurrency=4,
                navigator_languages=False,
                navigator_permissions=True,
                navigator_platform=False,
                navigator_plugins=True,
                navigator_user_agent=False,
                navigator_vendor=False,
                outerdimensions=True,
                hairline=False,
            ),
        )

        if blocked_resources is not None:
            await page.route(
                "**/*",
                lambda route: asyncio.create_task(
                    block_resources_and_sentry(route, blocked_resources),
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

        await page.screenshot(path=path)

    @classmethod
    async def create(cls, headless: bool = True):
        self = Client()
        await self.init_browser(headless=headless)

        return self
