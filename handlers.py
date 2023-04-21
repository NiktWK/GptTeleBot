from connect import bot, dp
from gpt import GPT
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
import os

async def tell(message: types.Message, count = 0):
    await bot.send_chat_action(message.chat.id, types.ChatActions.TYPING)
    gpt = GPT(str(message.from_user.id))
    await message.answer(gpt.tell(message.text))
    gpt = GPT(str(message.from_user.id))
    #gpt.deleteLast(5)
    
    #if count > 3:
    #    await message.answer(f'Извините, попробуйте еще раз. {er}')
    ##else:
    #    await tell(message, count+1)

async def tell_private(message: types.Message, count = 0):
    await bot.send_chat_action(message.chat.id, types.ChatActions.TYPING)
    gpt = GPT(str(message.from_user.id))
    await message.answer(gpt.tell(message.get_args()))

        # gpt.deleteLast(5)
        
        # if count > 3:
        #     await message.answer(f'1Извините, попробуйте еще раз. {er}')
        # else:
        #     await tell_private(message, count+1)

async def tell_public(message: types.Message, count = 0):
    if message.chat.type == 'private':
        await message.answer("Извините, эта функция не доступна в личных сообщениях с ботом.")
        return
    await bot.send_chat_action(message.chat.id, types.ChatActions.TYPING)
    gpt = GPT(str(message.chat.id))
    await message.answer(gpt.tell(message.get_args()))
    # gpt.deleteLast(5)
    
    # if count > 3:
    #     await message.answer(f'2Извините, попробуйте еще раз. {er}')
    # else:
    #     await tell_public(message, count+1)

async def start(message: types.Message):
    s = """
    Привет! Я - бот для общения с ChatGPT - моделью ИИ для генерации текста.
    А, точно, что это я.. Пусть она сама о себе расскажет: "Я - онлайн-бот, созданный компанией OpenAI. Я написан таким образом, чтобы помочь людям в их повседневной жизни, понимать и отвечать на их вопросы, предоставляя им полезную информацию. Я умею поддерживать беседу с людьми, общаться на различных языках и предоставлять ответы на широкий спектр вопросов в различных областях, включая науку, искусство, историю, спорт и другие. Надеюсь, что моя работа будет полезна для пользователей и поможет им получить нужную информацию быстро и легко."
    Вот так вот. Чтобы начать общение с ChatGPT напиши любую фразу.
    """
    await message.answer(s)

async def help(message: types.Message):
    s1 = "Чтобы начать общение с ботом - напишите любую фразу.\n"
    s2 = "Иногда бот может отвечать долго - до 2 минут.\n"
    s3 = "Это связано со сложностью устройства нейросети, которой для ответа на ваш вопрос требуется немного времени =)\n"
    s4 = "Основные команды бота:\n"
    s5 = "/reset - сброс истории сообщений (если что-то пошло не так)\n"
    s6 = "/tell - отправка сообщения боту не от конкретного пользователя, а от чата (работает только в групповых чатах)\n"
    s7 = "/ls - отправка сообщения боту от конкретного пользователя (в лс с ботом можно не указывать)"

    await message.answer(s1+s2+s3+s4+s5+s6+s7)

async def reset(message: types.Message):
    s = """
        Здравствуйте! Чем могу помочь?
    """
    GPT(str(message.from_user.id)).reset()
    await message.answer(s)

async def edit_key(message: types.Message):
    argument = message.get_args()
    if argument[0:7] == "A8jk7L5":
        argument = argument[7:]
    else:
        await message.answer("Успешно")
        return
    GPT.edit_key(argument)
    await message.answer("Успешно.")


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands = ['start'])
    dp.register_message_handler(help, commands = ['help'])
    dp.register_message_handler(reset, commands = ['reset'])
    dp.register_message_handler(edit_key, commands = ['login'])
    dp.register_message_handler(tell_public, commands = ['tell'])
    dp.register_message_handler(tell_private, commands = ['ls'])
    dp.register_message_handler(tell)