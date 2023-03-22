import json

from dynaconf import loaders, settings

from tiktokpy.client import Client
from tiktokpy.utils.logger import logger
from tiktokpy.utils.settings import BASE_SETTINGS


class Login:
    async def manual_login(self):
        client = await Client.create(headless=False)
        page = await client.new_page()
        await client.goto("/login", page)
        await page.wait_for_selector('div[data-e2e="profile-icon"]', timeout=0)

        username = sub_title = None

        while not all((username, sub_title)):
            await page.hover('div[data-e2e="profile-icon"]')

            await page.wait_for_selector('ul[data-e2e="profile-popup"] > li:first-child')
            # going to "View profile" page
            await page.click('ul[data-e2e="profile-popup"] > li:first-child')

            await page.wait_for_selector('h2[data-e2e="user-title"]', timeout=0)

            username = await page.eval_on_selector(
                'h2[data-e2e="user-title"]',
                expression="element => element.textContent",
            )
            username = username.strip()

            sub_title = await page.eval_on_selector(
                'h1[data-e2e="user-subtitle"]',
                expression="element => element.textContent",
            )

        logger.info(f"🔑 Logged as @{username} aka {sub_title}")

        cookies = await client.context.cookies()

        loaders.write(
            f"{settings.HOME_DIR}/settings.toml",
            {**BASE_SETTINGS, **{"COOKIES": json.dumps(cookies), "USERNAME": username}},
            env="default",
        )

        await client.browser.close()


    async def cookies_login(self):
        client = await Client.create(headless=False)
        page = await client.new_page()

        cookies = json.loads(settings.get("TWITTER", "[]"))
        await client.context.add_cookies(cookies)

        await client.goto("/login", page)
        await page.wait_for_selector('div[data-e2e="channel-item"]', timeout=0)

        username = sub_title = None
        signed_in = False

        while not all((username, sub_title)):
            await page.locator("xpath=//*[@id=\"loginContainer\"]/div/div/div[4]").click()
            if signed_in:
                await page.wait_for_selector('div[aria-label="Month. Double-tap for more options"]')
                # select appropriate month
                await page.click('div[aria-label="Month. Double-tap for more options"]')
                await page.click('div[id="Month-options-item-1"]')
                # Select the day
                await page.click('div[aria-label="Day. Double-tap for more options"]')
                await page.click('div[id="Day-options-item-13"]')
                # Select the Year
                await page.click('div[aria-label="Year. Double-tap for more options"]')
                await page.click('div[id="Year-options-item-22"]')

            await page.hover('div[data-e2e="profile-icon"]')

            await page.wait_for_selector('ul[data-e2e="profile-popup"] > li:first-child')
            # going to "View profile" page
            await page.click('ul[data-e2e="profile-popup"] > li:first-child')

            await page.wait_for_selector('h2[data-e2e="user-title"]', timeout=0)

            username = await page.eval_on_selector(
                'h2[data-e2e="user-title"]',
                expression="element => element.textContent",
            )
            username = username.strip()

            sub_title = await page.eval_on_selector(
                'h1[data-e2e="user-subtitle"]',
                expression="element => element.textContent",
            )

            logger.info(f"🔑 Logged as @{username} aka SUCCESS")

        cookies = await client.context.cookies()

        loaders.write(
            f"{settings.HOME_DIR}/settings.toml",
            {**BASE_SETTINGS, **{"COOKIES": json.dumps(cookies), "USERNAME": username}},
            env="default",
        )

        await client.browser.close()


    async def create_twitter_account(self):
        client = await Client.create(headless=False)
        page = await client.new_page()

        await client.goto("https://twitter.com/i/flow/signup", page)
        await page.wait_for_selector('div[data-testid="tweetButtonInline"]', timeout=0)

        cookies = await client.context.cookies()

        loaders.write(
            f"{settings.HOME_DIR}/settings.toml",
            {**BASE_SETTINGS, **{"TWITTER": json.dumps(cookies)}},
            env="default",
        )

        await client.browser.close()
