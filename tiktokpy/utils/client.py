from typing import List

from loguru import logger


async def block_resources(request, types: List[str]):
    if request.resourceType in types:
        await request.abort()
    else:
        await request.continue_()


async def catch_response_and_store(response, result):
    if "/item_list" in response.url:
        logger.debug(response.url)
        data = await response.json()

        for item in data["items"]:
            result.append(item)
        logger.debug(f"🛒Collected {len(data['items'])} items. Total: {len(result)}")
