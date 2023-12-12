import asyncio, for_data.gpt
from handlers.handlers import register_handlers
from handlers.handlers_reply import *
from connect import bot, dp, set_commands
import aiohttp

async def main():
    global bot, dp
    register_handlers(dp)
    await set_commands(bot)
    await dp.start_polling()
    aiohttp.ClientSession().close()

if __name__ == '__main__':
    asyncio.run(main())