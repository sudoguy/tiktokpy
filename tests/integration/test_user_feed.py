import pytest
from loguru import logger

from tiktokpy import TikTokPy
from tiktokpy.models.feed import FeedItem


@pytest.mark.asyncio()
async def test_user_feed(bot: TikTokPy):
    feed = await bot.user_feed(username="@mileycyrus")
    logger.info(feed)

    assert len(feed) == 50
    assert isinstance(feed[0], FeedItem)
