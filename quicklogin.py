import asyncio

from tiktokpy import TikTokPy


async def main():
    async with TikTokPy() as bot:
        # create Twitter account
        await bot.create_twitter()
        # Sign up with created twitter account
        await bot.login_with_twitter()
        #
#captcha_verify_img--wrapper sc-gZMcBi jzVByM
asyncio.run(main())
