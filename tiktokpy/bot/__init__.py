import typing
from datetime import datetime
from types import TracebackType
from typing import List, Optional

import humanize
from dynaconf import settings

from tiktokpy.client import Client
from tiktokpy.client.login import Login
from tiktokpy.client.trending import Trending
from tiktokpy.client.user import User
from tiktokpy.models.feed import FeedItem, FeedItems
from tiktokpy.utils.logger import init_logger, logger
from tiktokpy.utils.settings import load_or_create_settings

from .version import __version__


class TikTokPy:
    def __init__(self, settings_path: Optional[str] = None):
        init_logger()
        self.started_at = datetime.now()
        self.client: Client

        logger.info("🥳 TikTokPy initialized. Version: {}", __version__)

        load_or_create_settings(path=settings_path)

        if settings.get("COOKIES") and settings.get("USERNAME"):
            logger.info(f"✅ Used cookies of @{settings.USERNAME}")
        else:
            logger.info("🛑 Cookies not found, anonymous mode")

    async def __aenter__(self):
        await self.init_bot()

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
        logger.info(
            "✋ TikTokPy finished working. Session lasted: {}",
            humanize.naturaldelta(datetime.now() - self.started_at),
        )

    async def trending(self, amount: int = 50, lang: str = "en") -> List[FeedItem]:
        logger.info("📈 Getting trending items")
        items = await Trending(client=self.client).feed(amount=amount, lang=lang)

        logger.info(f"📹 Found {len(items)} videos")
        _trending = FeedItems(__root__=items)

        return _trending.__root__

    async def follow(self, username: str):
        username = f"@{username.lstrip('@')}"
        await User(client=self.client).follow(username=username)

    async def like(self, feed_item: FeedItem):
        await User(client=self.client).like(
            username=feed_item.author.username,
            video_id=feed_item.id,
        )

    async def unlike(self, feed_item: FeedItem):
        await User(client=self.client).unlike(
            username=feed_item.author.username,
            video_id=feed_item.id,
        )

    async def unfollow(self, username: str):
        username = f"@{username.lstrip('@')}"
        await User(client=self.client).unfollow(username=username)

    async def login_session(self):
        await Login().manual_login()

    async def user_feed(self, username: str, amount: int = 50) -> List[FeedItem]:
        username = f"@{username.lstrip('@')}"
        logger.info(f"📈 Getting {username} feed")
        items = await User(client=self.client).feed(username=username, amount=amount)

        logger.info(f"📹 Found {len(items)} videos")
        feed = FeedItems(__root__=items)

        return feed.__root__

    async def init_bot(self):
        self.client: Client = await Client.create(headless=True)

    @classmethod
    async def create(cls):
        self = TikTokPy()
        await self.init_bot()

        return self

    async def screenshot(self, page, name=""):
        filename = f"{name}_{datetime.now()}".lstrip("_")

        await self.client.screenshot(
            path=f"{settings.HOME_DIR}/screenshots/{filename}.png",
            page=page,
        )
