from aiogram import types, F, Router

from state import invited_users, user_joins

router = Router()



@router.message(F.new_chat_members)
async def check_new_members(message: types.Message):
    for user in message.new_chat_members:
        user_id = str(user.id)

        if user_id not in invited_users:
            await message.bot.ban_chat_member(
                chat_id=message.chat.id,
                user_id=user.id
            )

            await message.bot.unban_chat_member(
                chat_id=message.chat.id,
                user_id=user.id,
                only_if_banned=True
            )

            await message.answer(
                f"{user.full_name} удалён: нахуй с чата если не по ссылке от бота."
            )

        else:
            invited_users.discard(user_id)

            user_joins[user.id] = user_joins.get(user.id, 0) + 1

            await message.answer(
                f"👋 Добро пожаловать, {user.full_name}!\n"
                f"Ты зашла {user_joins[user.id]} раз(а).\n"
            )