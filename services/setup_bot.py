from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from services.config import BOT_TOKEN, DATABASE_PATH
from database.sqlite_db import DatabaseManager


bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = DatabaseManager(DATABASE_PATH)