import json

from dynaconf import loaders, settings

from tiktokpy.client import Client
from tiktokpy.utils.logger import logger
from tiktokpy.utils.settings import BASE_SETTINGS


class Login:
    async def manual_login(self):
        client = await Client.create(headless=False)
        page = await client.new_page()

        await client.stealth(page)

        await client.goto("/login", page)
        await page.waitForSelector(".profile", options={"timeout": 0})
        await page.hover(".avatar")

        await page.waitFor(".profile-actions > li:first-child")
        # going to "View profile" page
        await page.click(".profile-actions > li:first-child")
        await page.waitForSelector(".share-title", options={"timeout": 0})

        username = await page.Jeval(".share-title", pageFunction="element => element.textContent")
        username = username.strip()

        sub_title = await page.Jeval(
            ".share-sub-title", pageFunction="element => element.textContent",
        )

        logger.info(f"🔑 Logged as @{username} aka {sub_title}")

        cookies = await page.cookies()

        loaders.write(
            f"{settings.HOME_DIR}/settings.toml",
            {**BASE_SETTINGS, **{"COOKIES": json.dumps(cookies), "USERNAME": username}},
            env="default",
        )

        await client.browser.close()
