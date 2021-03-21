import pytest
from loguru import logger

from tiktokpy import TikTokPy
from tiktokpy.models.feed import FeedItem


@pytest.mark.asyncio()
async def test_trending(bot: TikTokPy):
    trending = await bot.trending(amount=1)
    logger.info(trending)

    assert len(trending) == 1
    assert isinstance(trending[0], FeedItem)
