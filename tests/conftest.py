import pytest

from tiktokpy import TikTokPy


@pytest.fixture()
async def bot() -> TikTokPy:
    async with TikTokPy() as bot:
        yield bot
