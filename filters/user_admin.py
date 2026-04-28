from aiogram.filters import BaseFilter
from aiogram.types import Message


class UserAdminFilter(BaseFilter):
    def __init__(self, allow_owner: bool = True):
        self.allow_owner = allow_owner

    async def __call__(self, message: Message) -> bool:
        member = await message.bot.get_chat_member(
            message.chat.id,
            message.from_user.id
        )

        if member.status == "administrator":
            return True

        if self.allow_owner and member.status == "creator":
            return True

        return False