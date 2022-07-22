<h1 align="center" style="font-size: 3rem;">
TikTokPy
</h1>
<p align="center">
 <em>Tooling that <b>automates</b> your social media interactions to “farm” Likes and Followers on TikTok</em></p>

<p align="center">
<a href="https://travis-ci.com/sudoguy/tiktokpy">
    <img src="https://travis-ci.com/sudoguy/tiktokpy.svg?branch=master" alt="Build Status">
</a>
<a href="https://pypi.org/project/tiktokpy/">
    <img src="https://badge.fury.io/py/tiktokpy.svg" alt="Package version">
</a>
</p>

---

## Quickstart.py

```python
import asyncio
from tiktokpy import TikTokPy


async def main():
    async with TikTokPy() as bot:
        # Do you want to get trending videos? You can!
        trending_items = await bot.trending(amount=5)

        for item in trending_items:
            # ❤️ you can like videos
            await bot.like(item)
            # or unlike them
            await bot.unlike(item)
            # or follow users
            await bot.follow(item.author.username)
            # as and unfollow
            await bot.unfollow(item.author.username)

        # 😏 getting user's feed
        user_feed_items = await bot.user_feed(username="justinbieber", amount=5)

        for item in user_feed_items:
            # 🎧 get music title, cover, link, author name..
            print("Music title: ", item.music.title)
            # #️⃣ print all tag's title of video
            print([tag.title for tag in item.challenges])
            # 📈 check all video stats
            print("Comments: ", item.stats.comments)
            print("Plays: ", item.stats.plays)
            print("Shares: ", item.stats.shares)
            print("Likes: ", item.stats.likes)

        # and many other things 😉


asyncio.run(main())
```

## Installation

Install with pip:

```shell
pip install tiktokpy
```

Install browser by playwright

```shell
playwright install chromium
```

If you have little to no knowledge in programming: Read this Guide ["How to use TiktokPy Python Bot"](https://my-tailwind-nextjs-starter-blog.vercel.app/blog/how-to-use-tiktokpy-for-beginner-programmers-indepth-guide) for beginners

## Run

To create your cookies and settings.toml file simply run

```shell
python quicklogin.py
```
and then after you login run

```shell
python quickstart.py
```