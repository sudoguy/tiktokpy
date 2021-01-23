from typing import List

from tiktokpy.utils.logger import logger


async def block_resources_and_sentry(request, types: List[str]):
    is_blocked = False

    if request.resourceType in types:
        is_blocked = True

    if "/sentry/" in request.url:
        is_blocked = True

    if is_blocked:
        await request.abort()
    else:
        await request.continue_()


async def catch_response_and_store(response, result):
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
