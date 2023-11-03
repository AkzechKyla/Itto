import logging
from typing import TYPE_CHECKING, Any
import discord

if TYPE_CHECKING:
    from Itto.discord import Bot


class Embed(discord.Embed):
    def __init__(self, bot: "Bot", title: str, **kwargs: Any) -> None:
        if kwargs.get("color") is None:
            kwargs["color"] = bot.color

        super().__init__(title=title, **kwargs)


class ErrorEmbed(discord.Embed):
    def __init__(self, record: logging.LogRecord, **kwargs: Any) -> None:
        super().__init__(
            title=record.levelname,
            description=f"**{record.name}** in module `{record.pathname}` at line **{record.lineno}**",
            color=discord.Colour.from_rgb(255, 8, 8),
            **kwargs,
        )
        self.add_field(
            name="Message",
            value=f"```{record.message[max(0, len(record.message) - 1018):]}```",
        )
        self.set_footer(text=record.asctime)
