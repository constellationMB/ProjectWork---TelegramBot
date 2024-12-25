from aiogram import Router, types
from aiogram.filters import CommandStart

from utils.request import check_text_with_languagetool, check_text_with_spacy, \
    check_text_with_openai, check_and_improve_with_languagetool
from loguru import logger

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.reply("Привет, " + message.from_user.full_name + "! Я бот, созданный @Const_the_night_kv (в рамках проектной работы)!")
    await message.answer("Я помогу тебе проверить текст на ошибки! Введи текст для проверки:")


@router.message()
async def checker(message: types.Message):
    try:
        corrected_text = check_and_improve_with_languagetool(message.text)
        language_tool = check_text_with_languagetool(message.text)
        await message.reply("<b>Версия LanguageTool: </b>\n\n" + language_tool[0])
        await message.reply("<b>Рекомендация от LanguageTool: </b>\n\n" + corrected_text)
        await message.reply("<b>Разбор на основе SpaCy: </b>\n\n" + check_text_with_spacy(message.text))
        await message.reply("<b>Мнение ChatGPT: </b>\n\n" + check_text_with_openai(message.text))
        logger.info(f"Пользователь @{message.from_user.username} получил ответ на текст: {message.text}")
    except Exception as e:
        logger.error("Ошибка при проверке текста у пользователя @" + str(message.from_user.username) + ": " + str(e))
        await message.reply("Произошла ошибка при проверке текста")
