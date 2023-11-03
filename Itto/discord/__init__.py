import os
import glob
import asyncio
import logging
from typing import cast, Any
import discord
from discord.ext import commands as dc
from Itto.cai import CharacterAI
from Itto.logging import get_logger
from Itto.discord.embeds import ErrorEmbed


class Bot(dc.Bot):
    def __init__(self, *, loop: asyncio.AbstractEventLoop) -> None:
        super().__init__(
            loop=loop,
            command_prefix="itto ",
            help_command=None,
            intents=discord.Intents.all(),
        )
        self.color = discord.Colour.from_rgb(245, 224, 66)
        self.ai = CharacterAI("TKuU0oDYJ3QfF4InA6C2jwK8pmqecERMYuJ7FLHXEHU")

        for name in dir(self):
            if name.startswith("_on_") and name.endswith("_event"):
                self._add_event(name.lstrip("_").rstrip("_event"))

    def _add_event(self, event_name: str) -> None:
        event = getattr(self, f"_{event_name}_event")

        async def event_wrapper(*args: Any, **kwargs: Any) -> None:
            try:
                await event(*args, **kwargs)
            except Exception as error:
                get_logger(f"Bot.{event_name}").exception(error)
                raise error

        self.add_listener(event_wrapper, event_name)

    async def start(self, token: str, *, reconnect: bool = True) -> None:
        await self.ai.initialize()

        # Load cogs
        for path in glob.iglob(
            os.path.join("watdo", "discord", "cogs", "**", "*"),
            recursive=True,
        ):
            if path.endswith("__init__.py"):
                continue

            if path.endswith(".py"):
                path = path.rstrip(".py").replace("/", ".").replace("\\", ".")
                await self.load_extension(path)

        # Ensure docstring for all commands
        for cog in self.cogs.values():
            for command in cog.get_commands():
                if command.help is None:
                    raise Exception(
                        f"Please add docstring for {command.module}.{command.name}"
                    )

        await super().start(token, reconnect=reconnect)

    async def _on_ready_event(self) -> None:
        logger = get_logger("Bot.on_ready")
        logger.info("Arataki Itto is ready!!")

    async def _on_command_error_event(
        self, ctx: dc.Context["Bot"], error: dc.CommandError
    ) -> None:
        if isinstance(error, dc.CommandNotFound):
            await self.send(ctx, f'No command "{ctx.invoked_with}" ❌')
        else:
            await self.send(ctx, f"**{type(error).__name__}:** {error}")

    async def on_message(self, message: discord.Message) -> None:
        try:
            bot_user = cast(discord.User, self.user)

            if message.author.id == bot_user.id:
                return

            if message.channel.id == 1169974916754440252:
                async with message.channel.typing():
                    reply = await self.ai.send(message.content)

                await self.send(message.channel, reply)
                return

            if not message.content.startswith(str(self.command_prefix)):
                if bot_user.mention in message.content.replace("<@!", "<@"):
                    await self.send(message.channel, "Hey compadre!")

            else:
                await self.process_commands(message)
        except Exception as error:
            get_logger("Bot.on_message").exception(error)
            raise error

    @staticmethod
    async def send(
        messageable: discord.abc.Messageable,
        content: Any = None,
        *args: Any,
        **kwargs: Any,
    ) -> discord.Message:
        if content is None:
            return await messageable.send(*args, **kwargs)

        return await messageable.send(str(content)[:2000], *args, **kwargs)

    def log(self, record: logging.LogRecord) -> None:
        channel = cast(discord.TextChannel, self.get_channel(1086519345972260894))
        self.loop.create_task(self.send(channel, embed=ErrorEmbed(record)))
