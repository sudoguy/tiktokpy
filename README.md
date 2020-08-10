<h1 align="center" style="font-size: 3rem;">
TikTokPy
</h1>
<p align="center">
 <em>Tooling that <b>automates</b> your social media interactions to “farm” Likes and Followers on TikTok</em></p>

<p align="center">
<a href="https://travis-ci.org/sudoguy/tiktokpy">
    <img src="https://travis-ci.org/sudoguy/tiktokpy.svg?branch=master" alt="Build Status">
</a>
<a href="https://pypi.org/project/tiktokpy/">
    <img src="https://badge.fury.io/py/tiktokpy.svg" alt="Package version">
</a>
</p>

---

## Quickstart

```python
import asyncio
from tiktokpy import TikTokPy


async def main():
    async with TikTokPy() as bot:
        # Do you want to get trending videos? You can!
        trending_items = await bot.trending(amount=100)

        for item in trending_items:
            # ❤️ you can like videos
            await bot.like(item)
            # or unlike them
            await bot.unlike(item)
            # or follow users
            await bot.follow(item.author.username)
            # as and unfollow
            await bot.unfollow(item.author.username)

            # 📹 also get ORIGINAL video urls without watermark
            print(item.video.original_video_url)

        # 😏 getting user's feed
        user_feed_items = await bot.user_feed(username="justinbieber", amount=30)

        for item in user_feed_items:
            # 🎧 get music title, cover, link, author name..
            print(item.music.title)
            # #️⃣ print all tag's title of video
            print([tag.title for tag in item.challenges])
            # 📈 check all video stats
            print(item.stats.comments)
            print(item.stats.plays)
            print(item.stats.shares)
            print(item.stats.likes)

        # and many other things 😉


asyncio.run(main())
```

## Installation

Install with pip:

```shell
pip install tiktokpy
```
