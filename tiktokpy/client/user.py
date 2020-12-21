import asyncio
from typing import List

from pyppeteer.page import Page
from tqdm import tqdm

from tiktokpy.client import Client
from tiktokpy.utils.client import catch_response_and_store, catch_response_info
from tiktokpy.utils.logger import logger


class User:
    def __init__(self, client: Client):
        self.client = client

    async def like(self, username: str, video_id: str):
        page: Page = await self.client.new_page(blocked_resources=["image", "media", "font"])
        logger.debug(f"👥 Like video id {video_id} of @{username}")

        like_info_queue: asyncio.Queue = asyncio.Queue(maxsize=1)

        page.on(
            "response",
            lambda res: asyncio.create_task(
                catch_response_info(res, like_info_queue, "/commit/item/digg"),
            ),
        )

        logger.info(f"🧭 Going to @{username}'s video {video_id} page for like")

        await self.client.goto(
            f"/@{username}/video/{video_id}",
            page=page,
            options={"waitUntil": "networkidle0"},
        )

        like_selector = ".lazyload-wrapper:first-child .item-action-bar.vertical > .bar-item-wrapper:first-child"  # noqa: E501
        is_liked = await page.J(f'{like_selector} svg[fill="none"]')

        if is_liked:
            logger.info(f"😏 @{username}'s video {video_id} already liked")
            return

        await page.click(like_selector)

        like_info = await like_info_queue.get()

        if like_info["status_code"] == 0:
            logger.info(f"👍 @{username}'s video {video_id} liked")
        else:
            logger.warning(f"⚠️  @{username}'s video {video_id} probably not liked")

        await page.close()

    async def unlike(self, username: str, video_id: str):
        page: Page = await self.client.new_page(blocked_resources=["image", "media", "font"])
        logger.debug(f"👥 Unlike video id {video_id} of @{username}")

        like_info_queue: asyncio.Queue = asyncio.Queue(maxsize=1)

        page.on(
            "response",
            lambda res: asyncio.create_task(
                catch_response_info(res, like_info_queue, "/commit/item/digg"),
            ),
        )

        logger.info(f"🧭 Going to @{username}'s video {video_id} page for unlike")

        await self.client.goto(
            f"/@{username}/video/{video_id}",
            page=page,
            options={"waitUntil": "networkidle0"},
        )

        like_selector = ".lazyload-wrapper:first-child .item-action-bar.vertical > .bar-item-wrapper:first-child"  # noqa: E501
        is_unliked = await page.J(f'{like_selector} svg[fill="currentColor"]')

        if is_unliked:
            logger.info(f"😏 @{username}'s video {video_id} already unliked")
            return

        await page.click(like_selector)

        like_info = await like_info_queue.get()

        if like_info["status_code"] == 0:
            logger.info(f"👎 @{username}'s video {video_id} unliked")
        else:
            logger.warning(f"⚠️  @{username}'s video {video_id} probably not unliked")

        await page.close()

    async def follow(self, username: str):
        page: Page = await self.client.new_page(blocked_resources=["image", "media", "font"])
        logger.debug(f"👥 Follow {username}")

        follow_info_queue: asyncio.Queue = asyncio.Queue(maxsize=1)

        page.on(
            "response",
            lambda res: asyncio.create_task(
                catch_response_info(res, follow_info_queue, "/commit/follow/user"),
            ),
        )

        logger.info(f"🧭 Going to {username}'s page for following")

        await self.client.goto(
            f"/@{username.lstrip('@')}",
            page=page,
            options={"waitUntil": "networkidle0"},
        )

        follow_title: str = await page.Jeval(
            ".follow-button",
            pageFunction="element => element.textContent",
        )

        if follow_title.lower() != "follow":
            logger.info(f"😏 {username} already followed")
            return

        await page.click(".follow-button")

        follow_info = await follow_info_queue.get()

        if follow_info["status_code"] == 0:
            logger.info(f"➕ {username} followed")
        else:
            logger.warning(f"⚠️  {username} probably not followed")

        await page.close()

    async def unfollow(self, username: str):
        page: Page = await self.client.new_page(blocked_resources=["image", "media", "font"])
        logger.debug(f"👥 Unfollow {username}")

        unfollow_info_queue: asyncio.Queue = asyncio.Queue(maxsize=1)

        page.on(
            "response",
            lambda res: asyncio.create_task(
                catch_response_info(res, unfollow_info_queue, "/commit/follow/user"),
            ),
        )

        logger.info(f"🧭 Going to {username}'s page for unfollowing")

        await self.client.goto(
            f"/@{username.lstrip('@')}",
            page=page,
            options={"waitUntil": "networkidle0"},
        )

        follow_title: str = await page.Jeval(
            ".follow-button",
            pageFunction="element => element.textContent",
        )

        if follow_title.lower() != "following":
            logger.info(f"😏 {username} already unfollowed")
            return

        await page.click(".follow-button")

        unfollow_info = await unfollow_info_queue.get()

        if unfollow_info["status_code"] == 0:
            logger.info(f"➖ {username} unfollowed")
        else:
            logger.warning(f"⚠️  {username} probably not unfollowed")

        await page.close()

    async def feed(self, username: str, amount: int):
        page: Page = await self.client.new_page(blocked_resources=["image", "media", "font"])
        logger.debug(f"📨 Request {username} feed")

        result: List[dict] = []

        page.on(
            "response",
            lambda res: asyncio.create_task(catch_response_and_store(res, result)),
        )

        _ = await self.client.goto(f"/{username}", page=page, options={"waitUntil": "networkidle0"})
        logger.debug(f"📭 Got {username} feed")

        await page.waitForSelector(".video-feed-item", options={"visible": True})

        pbar = tqdm(total=amount, desc=f"📈 Getting {username} feed")
        pbar.n = min(len(result), amount)
        pbar.refresh()

        attempts = 0
        last_result = len(result)

        while len(result) < amount:
            logger.debug("🖱 Trying to scroll to last video item")
            await page.evaluate(
                """
                document.querySelector('.video-feed-item:last-child')
                    .scrollIntoView();
            """,
            )
            await page.waitFor(1_000)

            elements = await page.JJ(".video-feed-item")
            logger.debug(f"🔎 Found {len(elements)} items for clear")

            pbar.n = min(len(result), amount)
            pbar.refresh()

            if last_result == len(result):
                attempts += 1
            else:
                attempts = 0

            if attempts > 10:
                pbar.clear()
                pbar.total = len(result)
                logger.info(
                    f"⚠️  After 10 attempts found {len(result)} videos. "
                    f"Probably some videos are private",
                )
                break

            last_result = len(result)

            if len(elements) < 500:
                logger.debug("🔻 Too less for clearing page")
                continue

            await page.JJeval(
                ".video-feed-item:not(:last-child)",
                pageFunction="(elements) => elements.forEach(el => el.remove())",
            )
            logger.debug(f"🎉 Cleaned {len(elements) - 1} items from page")
            await page.waitFor(30_000)

        await page.close()
        pbar.close()
        return result[:amount]
