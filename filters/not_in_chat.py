from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.enums import ChatMemberStatus


class NotInTargetChat(BaseFilter):

    def __init__(self, chat_id: int):
        self.chat_id = chat_id

    async def __call__(self, message: Message) -> bool:
        member = await message.bot.get_chat_member(
            self.chat_id,
            message.from_user.id
        )

        return member.status in [
            ChatMemberStatus.LEFT,
            ChatMemberStatus.KICKED
        ]