import asyncio
from asyncio import Future
from characterai import PyAsyncCAI
from Itto.environ import CAI_TOKEN


class ChatInfo:
    def __init__(self, *, chat_id: str, creator_id: str) -> None:
        self.chat_id = chat_id
        self.creator_id = creator_id


class CharacterAI:
    def __init__(self, character_id: str) -> None:
        self.character_id = character_id
        self.client = PyAsyncCAI(CAI_TOKEN)
        self.chat_info: ChatInfo
        self.chat: PyAsyncCAI.chat2

    async def _connect(self, connected_future: Future[None]) -> None:
        async with self.client.connect() as chat2:
            self.chat = chat2
            connected_future.set_result(None)
            await Future()

    async def initialize(self) -> None:
        future: Future[None] = Future()
        chat_data = (await self.client.chat2.get_chat(self.character_id))["chats"][0]
        self.chat_info = ChatInfo(
            chat_id=chat_data["chat_id"],
            creator_id=chat_data["creator_id"],
        )
        asyncio.create_task(self._connect(future))
        await future

    async def send(self, message: str) -> str:
        try:
            data = await self.chat.send_message(
                self.character_id,
                self.chat_info.chat_id,
                message,
                {"author_id": self.chat_info.creator_id},
            )
            return data["turn"]["candidates"][0]["raw_content"]
        except RuntimeError:
            return "Please, slow down a bit."
