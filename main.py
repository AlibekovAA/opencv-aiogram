import os
import re
import asyncio
import logging
from dotenv import load_dotenv

from helper import blur_faces_or_eyes
from aiogram import Bot, Dispatcher, types
from aiogram.enums.parse_mode import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import ContentType, FSInputFile
from aiogram.enums.dice_emoji import DiceEmoji

load_dotenv()
BOT_TOKEN: str | None = os.getenv("BOT_TOKEN")

logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8', filemode='w')
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command('clear'))
async def cmd_clear(message: types.Message, bot: Bot) -> None:
    try:
        for i in range(message.message_id, 0, -1):
            await bot.delete_message(message.from_user.id, i)
    except TelegramBadRequest as ex:
        if ex.message == "Bad Request: message to delete not found":
            pass


@dp.message(Command('start'))
async def send_welcome(message: types.Message) -> None:
    await message.answer("Привет! Я твой помощник в обработке фотографий."
                         "Могу размыть лица и глаза на фото, обеспечивая конфиденциальность и безопасность. "
                         "Просто отправь мне фотографию, и я помогу сделать ее более анонимной.")
    logger.info(f"Бот запущен. Приветственное сообщение отправлено пользователю {
                message.from_user.id}")


@dp.message(Command('dice'))
async def cmd_dice(message: types.Message) -> None:
    await message.answer_dice(emoji=DiceEmoji.DICE)
    logger.info(f"Пользователь {message.from_user.id} запросил кубик")


@dp.message(Command('basketball'))
async def cmd__bask_ball(message: types.Message) -> None:
    await message.answer_dice(emoji=DiceEmoji.BASKETBALL)
    logger.info(f"Пользователь {
                message.from_user.id} запросил баскетбольный мяч")


@dp.message(Command('dart'))
async def cmd_dart(message: types.Message) -> None:
    await message.answer_dice(emoji=DiceEmoji.DART)
    logger.info(f"Пользователь {message.from_user.id} запросил дартс")


@dp.message(Command('football'))
async def cmd_foot_ball(message: types.Message) -> None:
    await message.answer_dice(emoji=DiceEmoji.FOOTBALL)
    logger.info(f"Пользователь {message.from_user.id} запросил футбольный мяч")


@dp.message(Command('jackpot'))
async def cmd_jackpot(message: types.Message) -> None:
    await message.answer_dice(emoji=DiceEmoji.SLOT_MACHINE)
    logger.info(f"Пользователь {message.from_user.id} запросил джекпот")


@dp.message(Command('bowling'))
async def cmd_bowling(message: types.Message) -> None:
    await message.answer_dice(emoji=DiceEmoji.BOWLING)
    logger.info(f"Пользователь {message.from_user.id} запросил боулинг")


@dp.message(Command('photo'))
async def send_bot_photo(message: types.Message):
    bot_info = await bot.get_me()
    bot_photo = await bot.get_user_profile_photos(user_id=bot_info.id)
    if bot_photo.photos:
        await bot.send_photo(chat_id=message.chat.id, photo=bot_photo.photos[0][0].file_id)
        logger.info(f"Отправлена фотография бота пользователю {
                    message.from_user.id}")
    else:
        await message.reply("У бота нет фотографии профиля.")
        logger.warning(f"Боту не удалось отправить фотографию пользователю {
                       message.from_user.id}")


@dp.message(Command('faces', 'eyes'))
async def blur_photo(message: types.Message):
    await message.answer("Пришли мне фотографию для размытия😊")
    logger.info(f"Получена команда на размытие {message.text[1:]} от пользователя {
                message.from_user.id}")


@dp.message()
async def handle_photo(message: types.Message):
    if message.content_type == ContentType.PHOTO:
        blur_type = 'faces'
        photo = message.photo[-1]
        photo_id = photo.file_id
        photo_path = f"{message.from_user.id}_{photo_id}.jpg"

        file_info = await bot.get_file(photo_id)
        photo_obj = await bot.download_file(file_info.file_path)
        with open(photo_path, 'wb') as photo_file:
            photo_file.write(photo_obj.read())

        with open('bot.log', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in reversed(lines):
                if 'faces' in line:
                    blur_type = 'faces'
                    break
                elif 'eyes' in line:
                    blur_type = 'eyes'
                    break

        blurred_photo_path = blur_faces_or_eyes(
            photo_path, blur_type=blur_type)

        await message.reply_photo(photo=FSInputFile(path=blurred_photo_path))

        os.remove(photo_path)
        os.remove(blurred_photo_path)
        logger.info(f"Фотография успешно обработана пользователем {
                    message.from_user.id}")


@dp.message()
async def check_message(message: types.Message) -> None:
    if message.text.lower() == 'привет':
        await message.answer(f"Hello, <b>{message.from_user.full_name}</b>😊", parse_mode=ParseMode.HTML)
        logger.info(f"Пользователь {
                    message.from_user.id} поприветствовал бота")
    elif message.text.lower() == 'пока':
        await message.answer('Пока! Если что-то понадобится, обращайтесь. 👋')
        logger.info(f"Пользователь {message.from_user.id} попрощался с ботом")
    else:
        pattern: re.Pattern[str] = re.compile(
            r'\bфото\b|\bфотография\b|\bфотка\b', flags=re.IGNORECASE)
        if not pattern.search(message.text):
            await message.reply('Я не знаю такую команду:(. Попробуй снова. 😕')
            logger.warning(f"Пользователь {
                           message.from_user.id} отправил неизвестную команду")
        else:
            await message.answer('Смотри в список команд. 📝')
            logger.info(f"Пользователь {
                        message.from_user.id} запросил список команд")


async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
