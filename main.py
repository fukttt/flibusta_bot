import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from utils.flibusta_crawler import Flibusta, Flibusta_Book
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.methods.edit_message_text import EditMessageText
from dotenv import load_dotenv

load_dotenv()

TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

class SelectedBook(StatesGroup):
    selected_book = State()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    kb = [
        [types.KeyboardButton(text="Поиск книги 📖")],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)

    await message.answer(
        f"Привет, {hbold(message.from_user.full_name)}!\nРад приветствовать тебя в нашем боте Flibusta Library.",
        reply_markup=keyboard,
    )


@dp.callback_query()
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer(callback.data)


@dp.message()
async def echo_handler(message: types.Message) -> None:
    try:
        if "Поиск книги" in message.text:
            await message.answer("Для того чтобы найти книгу напиши ее название мне.")
        else:
            mess = await message.reply("🔎 Секундочку, ищу")
            ff = Flibusta(9052, "127.0.0.1")
            if await ff.check_connection():
                books = await ff.search_for_books(query=message.text)

                builder = InlineKeyboardBuilder()
                for book in books:
                    builder.row(
                        types.InlineKeyboardButton(
                            text=f"📖 {book.name} - {book.author}",
                            callback_data="suka",
                        )
                    )
                if len(books) == 0:
                    await message.answer(
                        "не могу найти запрошенную книгу. Прошу прощения."
                    )
                else:
                    await bot(EditMessageText(chat_id=mess.chat.id,message_id=mess.message_id,
                        text="Найденные книги: ", reply_markup=builder.as_markup()
                    ))
            else:
                await message.answer("Что-то не так")
    except TypeError:
        await message.answer("Nice try!")


async def main() -> None:
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
