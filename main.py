from aiogram import Dispatcher, executor
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import (ChatType, ContentTypes, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)
from io import BytesIO
import aiohttp
from aiogram import Bot, types
from aiogram.utils.markdown import hbold, hlink
from aiogram.utils.exceptions import BadRequest
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from rich.logging import RichHandler
from datetime import datetime, date, time
import sqlite3
from pathlib import Path
from os.path import exists
from datetime import datetime
import os, sys
from aiogram.types import User



conn = sqlite3.connect('cicada.db')
cur = conn.cursor()

try:
    cur.execute('''CREATE TABLE cicada
               (name text, us_id text, link text, tt text)''')

    con.commit()
    print('\n\n\n\n     Создание БД')
except:
    pass
tt = datetime.now()


class PhotoStorage:
    def __init__(self, path: str):
        self.path = path
        self.data = self.load()
    
    def load(self):
        if exists(self.path):
            with open(self.path) as file:
                return file.readlines()
        
        with open(self.path, "w") as file:
            return list()
    
    def save(self):
        with open(self.path, "w") as file:
            return file.writelines(self.data)
    
    def add(self, user: User, url: str):
        
        if user.username: username = f"@{user.username}"
        else: username = f"ID={user.id}"
        
        self.data.append(f"{datetime.now()} {username}: {url} \n")
        return self.save()



ROOT_DIRECTORY = Path(__file__).parent.parent
try:
    TOKEN = open('sys', 'r').read()
    pass
except:
    print('\n   Это первый запуск Бота Установите Токен \n\n ')
    newe = open('sys', 'w').write(input('Token Bota:   '))
    TOKEN = open('sys', 'r').read()
    pass

photo_storage = PhotoStorage("_images")

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

async def upload_document(
    bot, doc: types.photo_size.PhotoSize or types.Document
) -> str:
    with await doc.download(BytesIO()) as file:

        form = aiohttp.FormData()
        form.add_field(
            name="file",
            value=file,
        )

        async with bot.session.post("https://telegra.ph/upload", data=form) as response:
            img_src = await response.json()

    return "http://telegra.ph/" + img_src[0]["src"]



@dp.message_handler(commands=['cicada'])
async def process_base(message: types.Message):
    chat_id = message.chat.id
    conn.close()
    with open("cicada.db", "rb") as doc:
        await bot.send_document(chat_id,
                                doc,
                                caption=f"📦 BACKUP\n"
                                        f"🕜 {tt}")
                                        
                                        
@dp.message_handler(commands=['start'])
async def start(m: Message):
    """Отвечает на старт"""

    await m.answer(
        f"🔱 Привет, **{m.from_user.first_name}** 🔱 Я Бот Фотохостинг ! "
        f"⚠️Используй только меня, остерегайся фэйков!⚠️ \n\n"
        f"🔱Просто отправь мне фотографию. Также, ее можно отправить документом.🔱"
    )

@dp.message_handler(content_types=['photo'])
async def photo_handler(m: Message):
    photo = m.photo[-1]

    # Send a chat action
    await m.bot.send_chat_action(m.chat.id, "upload_photo")

    # Upload and add into the storage instance
    link = await upload_document(m.bot, photo)
    photo_storage.add(m.from_user, link)

    # Reply with an answer
    await m.reply(
        f"✓ Изображение загружено \n{link}",
        disable_web_page_preview=True,
    )
    name = m.chat.username
    us_id = m.chat.id
    conn = sqlite3.connect('cicada.db')
    cur = conn.cursor()
    cur.execute(
        f"""INSERT INTO cicada VALUES('{name}', '{us_id}', '{link}', '{tt}')""")
    conn.commit()
@dp.message_handler(content_types=['document'])
async def document_handler(m: Message):
    doc = m.document

    # Check if the document is an image
    if not doc.mime_type.startswith("image"):
        return

    # Send a chat action
    await m.bot.send_chat_action(m.chat.id, "upload_photo")

    # Upload and add into the storage instance
    link = await upload_document(m.bot, doc)
    photo_storage.add(m.from_user, link)

    # Reply with an answer
    await m.reply(
        f"✓ Изображение загружено \n{link}",
        disable_web_page_preview=True,
    )


async def send_file(m: Message):
    with open(photo_storage.path) as file:
        try:
            await m.answer_document(file, caption="✓ Файл был отправлен")
        except BadRequest:
            await m.answer("✖ Ошибка: пустой файл.")


def setup(dp: Dispatcher):
    dp.register_message_handler(
        start, ChatTypeFilter(ChatType.PRIVATE), commands=["start", "help"]
    )

    dp.register_message_handler(
        send_file, ChatTypeFilter(ChatType.PRIVATE), commands="cicada"
    )

    dp.register_message_handler(
        photo_handler,
        ChatTypeFilter(ChatType.PRIVATE),
        content_types=ContentTypes.PHOTO,
    )

    dp.register_message_handler(
        document_handler,
        ChatTypeFilter(ChatType.PRIVATE),
        content_types=ContentTypes.DOCUMENT,
    )
    
try:
    if __name__ == "__main__":
        executor.start_polling(dp)
except:
    os.system('pip3 install poetry')
    os.system('poetry install')
    if __name__ == "__main__":
        executor.start_polling(dp)