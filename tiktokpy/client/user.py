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
            f"/@{username}/video/{video_id}", page=page, options={"waitUntil": "networkidle0"},
        )

        like_element = await page.J("span.like")

        if "liked" in like_element._remoteObject["description"]:
            logger.info(f"😏 @{username}'s video {video_id} already liked")
            return

        await page.click(".like-part")

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
            f"/@{username}/video/{video_id}", page=page, options={"waitUntil": "networkidle0"},
        )

        like_element = await page.J("span.like")

        if "liked" not in like_element._remoteObject["description"]:
            logger.info(f"😏 @{username}'s video {video_id} already unliked")
            return

        await page.click(".like-part")

        like_info = await like_info_queue.get()

        if like_info["status_code"] == 0:
            logger.info(f"👍 @{username}'s video {video_id} unliked")
        else:
            logger.warning(f"⚠️  @{username}'s video {video_id} probably not unliked")

        await page.close()

    async def follow(self, username: str):
        page: Page = await self.client.new_page(blocked_resources=["image", "media", "font"])
        logger.debug(f"👥 Follow {username}")

        logger.info(f"🧭 Going to {username}'s page for following")

        await self.client.goto(
            f"/@{username.lstrip('@')}", page=page, options={"waitUntil": "networkidle0"},
        )

        follow_title: str = await page.Jeval(
            ".follow-button", pageFunction="element => element.textContent",
        )

        if follow_title.lower() != "follow":
            logger.info(f"😏 {username} already followed")
            return

        await page.click(".follow-button")
        # ToDo: need to wait response from follow request
        await page.waitFor(3_000)

        updated_follow_title: str = await page.Jeval(
            ".follow-button", pageFunction="element => element.textContent",
        )

        if updated_follow_title.lower() != "follow":
            logger.info(f"➕ {username} followed")
        else:
            logger.warning(f"⚠️  {username} probably not followed")

        await page.close()

    async def unfollow(self, username: str):
        page: Page = await self.client.new_page(blocked_resources=["image", "media", "font"])
        logger.debug(f"👥 Unfollow {username}")

        logger.info(f"🧭 Going to {username}'s page for unfollowing")

        await self.client.goto(
            f"/@{username.lstrip('@')}", page=page, options={"waitUntil": "networkidle0"},
        )

        follow_title: str = await page.Jeval(
            ".follow-button", pageFunction="element => element.textContent",
        )

        if follow_title.lower() != "following":
            logger.info(f"😏 {username} already unfollowed")
            return

        await page.click(".follow-button")
        # ToDo: need to wait response from unfollow request
        await page.waitFor(3_000)

        updated_follow_title: str = await page.Jeval(
            ".follow-button", pageFunction="element => element.textContent",
        )

        if updated_follow_title.lower() == "follow":
            logger.info(f"➖ {username} unfollowed")
        else:
            logger.warning(f"⚠️  {username} probably not unfollowed")

        await page.close()

    async def feed(self, username: str, amount: int):
        page: Page = await self.client.new_page(blocked_resources=["image", "media", "font"])
        logger.debug(f"📨 Request {username} feed")

        result: List[dict] = []
        user_info_queue: asyncio.Queue = asyncio.Queue(maxsize=1)

        page.on(
            "response", lambda res: asyncio.create_task(catch_response_and_store(res, result)),
        )

        page.on(
            "response",
            lambda res: asyncio.create_task(
                catch_response_info(res, user_info_queue, "/user/detail"),
            ),
        )
        _ = await self.client.goto(f"/{username}", page=page, options={"waitUntil": "networkidle0"})
        logger.debug(f"📭 Got {username} feed")

        await page.waitForSelector(".video-feed-item", options={"visible": True})

        user_info = await user_info_queue.get()
        user_video_count = user_info["userInfo"]["stats"]["videoCount"]

        if user_video_count < amount:
            logger.info(
                f"⚠️  User {username} has only {user_video_count} videos. "
                f"Set amount from {amount} to {user_video_count}",
            )
            amount = user_video_count

        pbar = tqdm(total=amount, desc=f"📈 Getting {username} feed")

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
