from dotenv import load_dotenv
import os

import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ChatMemberStatus
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

import filters.chat_type
from filters.not_in_chat import NotInTargetChat



load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
TTYAN_CHAT_ID = os.getenv("TTYAN_CHAT_ID")
MELISKIN_ID = os.getenv("MELISKIN_ID")


logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"), filters.chat_type.ChatTypeFilter("private"), NotInTargetChat(TTYAN_CHAT_ID))
async def cmd_start(message: types.Message):
    print(f"заюзали старт чат айди, юзер айди: {message.chat.id, message.from_user.id}")
    await message.answer(
        f"Добрый день! Я бот для предоставления доступа к чату ттян. Чат предназначен для общение людей, совершающих или совершивших переход из-за гендерной дисфории.\n"
        f"Для участия в чате необходимо предоставить доказательства того, что Вы на HRT.\n"
        f"Этот чат безопасное место для трансгендерных девушек. Просим прощения за такое недоверие\n"
        )
    await asyncio.sleep(1)
    await message.answer(
        f"Для продолжения необходимо загрузить фотографию гормональных препаратов с бумажкой, на которой написано от руки:")
    await asyncio.sleep(1)
    await message.answer(
        f"@{message.from_user.username} {datetime.now().strftime('%I:%M %p')} /ttyn")
    await asyncio.sleep(1)
    await message.answer(
        f"Внимание! После загрузки фотографии с пруфом HRT она будет сразу же отправлена для ревизии. Это может занять от нескольких минут до нескольких часов. Пожалуйста, подождите")

@dp.message(Command("start"), filters.chat_type.ChatTypeFilter("private"))
async def cmd_start(message: types.Message):
    print(f"заюзали старт чат айди, юзер айди: {message.chat.id, message.from_user.id}")
    await message.answer(
        f"Ты уже в чате, иди ломай в другом месте.\n"
        )


@dp.message(F.photo, filters.chat_type.ChatTypeFilter("private"), NotInTargetChat(TTYAN_CHAT_ID))
async def request_access(message: types.Message):
    photo = message.photo[-1].file_id

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="апрувнуть",
                    callback_data=f"approve:{message.chat.id}:{message.from_user.id}"
                )
            ]
        ]
    )

    await message.bot.copy_message(
        chat_id=TTYAN_CHAT_ID,
        from_chat_id=message.chat.id,
        message_id=message.message_id,
        reply_markup=kb
    )




@dp.callback_query(F.data.startswith("approve:"))
async def approve_handler(callback: CallbackQuery):

    _, source_chat_id, user_id = callback.data.split(":")
    source_chat_id = int(source_chat_id)

    member = await callback.bot.get_chat_member(
        callback.message.chat.id,
        callback.from_user.id
    )

    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR] and member.user.id == MELISKIN_ID:
        await callback.answer("Не для вас написано, тегните админа если срочно надо", show_alert=True)
        return

    invite = await callback.bot.create_chat_invite_link(
        chat_id=TTYAN_CHAT_ID,
        member_limit=1,
        name=user_id,
        creates_join_request = False
    )

    await callback.bot.send_message(
        source_chat_id,
        f"Одноразовая ссылка на чат:\n{invite.invite_link}"
    )

    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.answer("Ссылка создана")

@dp.message(Command("ban"), F.reply_to_message)
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

@dp.message()
async def forward_all_messages(message: types.Message, bot):
    user = message.from_user
    user_id = user.id
    username = user.username or "нет username"
    message_id = message.message_id
    name = user.full_name

    text_info = (
        f"massage id:{message_id}:\n"\
        f"name: {name}\n"
        f"ID: {user_id}\n"
        f"Username: @{username}\n\n"
    )

    # если текст
    if message.text:
        await bot.send_message(
            MELISKIN_ID,
            text_info + f"💬 Сообщение:\n{message.text}"
        )
    else:
        await bot.send_message(MELISKIN_ID, text_info)
        try:
            await message.forward(MELISKIN_ID)
        except:
            await bot.copy_message(
                chat_id=MELISKIN_ID,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )



async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
