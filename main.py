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

from datetime import datetime, timedelta


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
TTYAN_CHAT_ID = os.getenv("TTYAN_CHAT_ID")
MELISKIN_ID = os.getenv("MELISKIN_ID")

invited_users = set()
last_photo_requests = {}
PHOTO_COOLDOWN = timedelta(minutes=10)
user_joins = {}


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
    user_id = message.from_user.id
    now = datetime.now()

    # Проверка кулдауна
    if user_id in last_photo_requests:
        elapsed = now - last_photo_requests[user_id]

        if elapsed < PHOTO_COOLDOWN:
            remaining = PHOTO_COOLDOWN - elapsed
            minutes = remaining.seconds // 60
            seconds = remaining.seconds % 60

            await message.answer(
                f"Фото уже отправлялось. Попробуйте через {minutes} мин {seconds} сек."
            )
            return

    # записываем время последней попытки
    last_photo_requests[user_id] = now

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="апрувнуть",
                    callback_data=f"approve:{message.chat.id}:{message.from_user.id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="дЁрнуть анус",
                    callback_data=f"reject:{message.chat.id}:{message.from_user.id}"
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

    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
        await callback.answer("Не для вас написано, тегните админа если срочно надо", show_alert=True)
        return

    invite = await callback.bot.create_chat_invite_link(
        chat_id=TTYAN_CHAT_ID,
        member_limit=1,
        name=user_id,
        creates_join_request = False
    )
    invited_users.add(str(user_id))
    print(invited_users)

    await callback.bot.send_message(
        source_chat_id,
        f"Одноразовая ссылка на чат:\n{invite.invite_link}"
    )

    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.answer("Ссылка создана")

@dp.callback_query(F.data.startswith("reject:"))
async def approve_handler(callback: CallbackQuery):

    _, source_chat_id, user_id = callback.data.split(":")
    source_chat_id = int(source_chat_id)

    member = await callback.bot.get_chat_member(
        callback.message.chat.id,
        callback.from_user.id)

    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
        await callback.answer("Не для вас написано, тегните админа если срочно надо", show_alert=True)
        return

    await callback.bot.send_message(
        source_chat_id,
        f"вас не приняли, идите нахуй"
    )
    await callback.message.edit_reply_markup(reply_markup=None)





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


@dp.message(F.new_chat_members)
async def check_new_members(message: types.Message):
    global total_joins

    for user in message.new_chat_members:
        user_id = str(user.id)

        # если НЕ по ссылке бота — кик
        if user_id not in invited_users:
            await bot.ban_chat_member(
                chat_id=message.chat.id,
                user_id=user.id
            )

            await bot.unban_chat_member(
                chat_id=message.chat.id,
                user_id=user.id,
                only_if_banned=True
            )

            await message.answer(
                f"{user.full_name} удалён: нахуй с чата если не по ссылке от бота."
            )

        else:
            # убираем одноразовый токен
            invited_users.discard(user_id)


            # персональный счётчик
            if user.id not in user_joins:
                user_joins[user.id] = 1
            else:
                user_joins[user.id] += 1

            await message.answer(
                f"👋 Добро пожаловать, {user.full_name}!\n"
                f"Ты зашла {user_joins[user.id]} раз(а).\n"
            )

# @dp.message()
# async def forward_all_messages(message: types.Message, bot):
#     user = message.from_user
#     user_id = user.id
#     username = user.username or "нет username"
#     message_id = message.message_id
#     name = user.full_name
#
#     text_info = (
#         f"massage id:{message_id}:\n"\
#         f"name: {name}\n"
#         f"ID: {user_id}\n"
#         f"Username: @{username}\n\n"
#     )
#
#     # если текст
#     if message.text:
#         await bot.send_message(
#             MELISKIN_ID,
#             text_info + f"💬 Сообщение:\n{message.text}"
#         )
#     else:
#         await bot.send_message(MELISKIN_ID, text_info)
#         try:
#             await message.forward(MELISKIN_ID)
#         except:
#             await bot.copy_message(
#                 chat_id=MELISKIN_ID,
#                 from_chat_id=message.chat.id,
#                 message_id=message.message_id
#             )
#


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
