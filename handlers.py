from connect import bot, dp
from gpt import GPT
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

async def tell(message: types.Message):
    try:
        print(message.text)
        await bot.send_chat_action(message.chat.id, types.ChatActions.TYPING)
        gpt = GPT(str(message.from_user.id))
        await message.answer(gpt.tell(message.text))
    except Exception as er:
        await message.answer(f'Извините, попробуйте еще раз. {er}')


async def start(message: types.Message):
    s = """
    Привет! Я - бот для общения с ChatGPT - моделью ИИ для генерации текста.
    А, точно, что это я.. Пусть она сама о себе расскажет: "Я - онлайн-бот, созданный компанией OpenAI. Я написан таким образом, чтобы помочь людям в их повседневной жизни, понимать и отвечать на их вопросы, предоставляя им полезную информацию. Я умею поддерживать беседу с людьми, общаться на различных языках и предоставлять ответы на широкий спектр вопросов в различных областях, включая науку, искусство, историю, спорт и другие. Надеюсь, что моя работа будет полезна для пользователей и поможет им получить нужную информацию быстро и легко."
    Вот так вот. Чтобы начать общение с ChatGPT напиши любую фразу.
    """
    await message.answer(s)

async def help(message: types.Message):
    s = """
    
    """
    await message.answer(s)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands = ['start'])
    dp.register_message_handler(tell)