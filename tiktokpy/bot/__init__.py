import logging
import sys
import typing
from datetime import datetime
from types import TracebackType
from typing import List

from loguru import logger

from tiktokpy.client import Client
from tiktokpy.client.trending import Trending
from tiktokpy.client.user import User
from tiktokpy.models.feed import FeedItem, FeedItems


class TikTokPy:
    def __init__(self):
        logging.disable(logging.CRITICAL)
        logger.remove()
        logger.add(sys.stdout, level=logging.INFO)
        logger.info("🥳 TikTokPy initialized")

    async def __aenter__(self):
        await self._init_bot()

        return self

    async def __aexit__(
        self,
        exc_type: typing.Type[BaseException] = None,
        exc_value: BaseException = None,
        traceback: TracebackType = None,
    ) -> None:
        logger.debug("🤔Trying to close browser..")

        await self.client.browser.close()

        logger.debug("✋ Browser successfully closed")
        logger.info("✋ TikTokPy stopped working..")

    async def trending(self, amount: int = 50, lang: str = "en") -> List[FeedItem]:
        logger.info("📈 Getting trending items")
        items = await Trending(client=self.client).feed(amount=amount, lang=lang)

        logger.info(f"📹 Found {len(items)} videos")
        _trending = FeedItems(__root__=items)

        return _trending.__root__

    async def user_feed(self, username: str, amount: int = 50) -> List[FeedItem]:
        username = f"@{username.lstrip('@')}"
        logger.info(f"📈 Getting {username} feed")
        items = await User(client=self.client).feed(username=username, amount=amount)

        logger.info(f"📹 Found {len(items)} videos")
        feed = FeedItems(__root__=items)

        return feed.__root__

    async def _init_bot(self):
        self.client: Client = await Client.create()

    @classmethod
    async def create(cls):
        self = TikTokPy()
        await self._init_bot()

        return self

    async def screenshot(self, page, name=""):
        filename = f"{name}_{datetime.now()}".lstrip("_")

        await self.client.screenshot(path=f"screenshots/{filename}.png", page=page)
