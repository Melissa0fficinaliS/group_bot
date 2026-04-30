from aiogram import Router, types
from aiogram.filters import Command

import filters.chat_type
from filters.not_in_chat import NotInTargetChat
from config import TTYAN_CHAT_ID
from datetime import datetime
import asyncio

router = Router()



@router.message(Command("start"), filters.chat_type.ChatTypeFilter("private"), NotInTargetChat(TTYAN_CHAT_ID))
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

@router.message(Command("start"), filters.chat_type.ChatTypeFilter("private"))
async def cmd_start(message: types.Message):
    print(f"заюзали старт чат айди, юзер айди: {message.chat.id, message.from_user.id}")
    await message.answer(
        f"Ты уже в чате, иди ломай в другом месте.\n"
        )
