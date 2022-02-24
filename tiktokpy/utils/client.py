from typing import List

from playwright.async_api import Response, Route

from tiktokpy.utils.logger import logger


async def block_resources_and_sentry(route: Route, types: List[str]):
    is_blocked = False

    if route.request.resource_type in types:
        is_blocked = True

    if "/sentry/" in route.request.url:
        is_blocked = True

    if is_blocked:
        await route.abort()
    else:
        await route.continue_()


async def catch_response_and_store(response: Response, result):
    if "/item_list" in response.url:
        logger.debug(response.url)
        data = await response.json()

        for item in data["itemList"]:
            result.append(item)
        logger.debug(f"🛒 Collected {len(data['items'])} items. Total: {len(result)}")


async def catch_response_info(response, queue, url: str):
    if url in response.url:
        logger.debug(response.url)
        result = await response.json()

        await queue.put(result)
        logger.debug(f"🛒 Collected response: {result}")
