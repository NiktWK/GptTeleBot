from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import config, os
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types.bot_command import BotCommand

bot = Bot(os.environ["TELEGRAM_BOT_TOKEN"])
dp = Dispatcher(bot, storage = MemoryStorage())

async def set_commands(bot : Bot):
    commands = [
        BotCommand('/help', 'Помощь'),
        BotCommand('/start', 'Привет')
    ]
    await bot.set_my_commands(commands)