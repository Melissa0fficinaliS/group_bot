from aiogram import Router

from aiogram import types, F
from aiogram.filters.command import Command

router = Router()



@router.message(Command("ban"), F.reply_to_message)
async def cmd_ban(message: types.Message):
    admins = await message.bot.get_chat_administrators(
        message.chat.id
    )

    admin_ids = {
        admin.user.id
        for admin in admins
    }

    # Только админы могут использовать команду
    if message.from_user.id not in admin_ids:
        await message.answer("не для вас команда")
        return

    target_id = message.reply_to_message.from_user.id
    # На всякий случай не баним бота
    if target_id == (await message.bot.me()).id:
        await message.answer("меня? смешная попытка")
        return

    # Нельзя банить себя
    if target_id == message.from_user.id:
        await message.answer("самобан это уже философия")
        return

    # Нельзя банить админов и владельца
    if target_id in admin_ids:
        await message.answer("админа банить нельзя")
        return

    try:
        await message.chat.ban(user_id=target_id)
        await message.answer("нахуй с чата")
    except Exception as e:
        await message.answer(f"не удалось забанить: {e}")

