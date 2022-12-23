import asyncio
import random
from typing import List, Optional

from dynaconf import settings
from tqdm import tqdm

from tiktokpy.client import Client
from tiktokpy.utils.client import catch_response_and_store
from tiktokpy.utils.logger import logger

FEED_LIST_ITEM = 'div[data-e2e="recommend-list-item-container"]'
FEED_LIST_ITEM_LAST_CHILD = f"{FEED_LIST_ITEM}:last-child"


class Trending:
    def __init__(self, client: Client, lang: Optional[str] = None):
        self.client = client
        self.lang = lang or settings.get("LANG")

    async def feed(self, amount: int):
        page = await self.client.new_page(blocked_resources=["media", "image", "font"])

        logger.debug('📨 Request "Trending" page')

        result: List[dict] = []

        page.on(
            "response",
            lambda res: asyncio.create_task(catch_response_and_store(res, result)),
        )
        _ = await self.client.goto(
            "/foryou",
            query_params={"lang": self.lang},
            page=page,
            wait_until="networkidle",
        )
        logger.debug('📭 Got response from "Trending" page')

        pbar = tqdm(total=amount, desc=f"📈 Getting trending {self.lang}")
        pbar.n = min(len(result), amount)
        pbar.refresh()

        try:
            while len(result) < amount:
                if len(result) != 0:
                    timeout = random.randint(5, 10)
                    await page.wait_for_timeout(timeout * 1000)

                logger.debug("🖱 Trying to scroll to last video item")

                await page.wait_for_selector(FEED_LIST_ITEM_LAST_CHILD)

                scroll_command = "document.querySelector('{selector}').scrollIntoView();"
                await page.evaluate(scroll_command.format(selector=FEED_LIST_ITEM_LAST_CHILD))
                await page.wait_for_timeout(1_000)

                elements = await page.query_selector_all(FEED_LIST_ITEM)
                logger.debug(f"🔎 Found {len(elements)} items on page")
                await self.client.screenshot("trending.png", page)

                pbar.n = min(len(result), amount)
                pbar.refresh()
        except Exception:
            logger.exception("Something went wrong. Interrupt work")

            # if len(elements) < 500:
            #     logger.debug("🔻 Too less for clearing page")
            #     continue

            # await page.eval_on_selector_all(
            #     f"{FEED_LIST_ITEM_CONTAINER}:not(:last-child)",
            #     expression="(elements) => elements.forEach(el => el.remove())",
            # )
            # logger.debug(f"🎉 Cleaned {len(elements) - 1} items from page")

        await page.close()
        pbar.close()
        return result[:amount]
