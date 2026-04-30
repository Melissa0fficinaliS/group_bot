from datetime import datetime

from aiogram import Router
from aiogram import types, F
from aiogram.enums import ChatMemberStatus
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

import filters.chat_type
from config import TTYAN_CHAT_ID
from filters.not_in_chat import NotInTargetChat
from state import last_photo_requests, PHOTO_COOLDOWN, invited_users

router = Router()

@router.message(F.photo, filters.chat_type.ChatTypeFilter("private"), NotInTargetChat(TTYAN_CHAT_ID))
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




@router.callback_query(F.data.startswith("approve:"))
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

@router.callback_query(F.data.startswith("reject:"))
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



