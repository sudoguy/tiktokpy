import typer

from tiktokpy import TikTokPy
from tiktokpy.cli.utils import coro

app = typer.Typer()


@app.command()
@coro
async def login():
    async with TikTokPy() as bot:
        await bot.login_session()


@app.callback()
def callback():
    pass
