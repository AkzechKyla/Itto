import asyncio
from Itto.discord import Bot
from Itto.environ import DISCORD_TOKEN


async def main(loop: asyncio.AbstractEventLoop) -> int:
    bot = Bot(loop=loop)

    await bot.start(DISCORD_TOKEN)

    return 0
