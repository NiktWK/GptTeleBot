from connect import bot, dp
from gpt import *
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from openai.error import RateLimitError
import aiohttp, asyncio, config, os
import requests

NOT_SHOW_AD_Q = 35
AD_STYLE = "<u>{header} </u>\n{text}"

async def ad(message: types.Message, id):
    ad = GPT(str(id)).ad()
    if ad and ad.image_path != 'None':
        await message.answer_photo(ad.image, caption = AD_STYLE.format(header = ad.header, text = ad.text), parse_mode='HTML')
    elif ad:
        await message.answer(AD_STYLE.format(header = ad.header, text = ad.text), parse_mode='HTML')

async def tell(message: types.Message, count = 0):
    ans = None
    try:
        await bot.send_chat_action(message.chat.id, types.ChatActions.TYPING)
        gpt = AsyncGPT(str(message.from_user.id))
        ans = await gpt.tell(message.text)
        await message.answer(ans)
        try:
            await ad(message, message.from_user.id)
        except Exception as er:
            await message.answer(f'Извините, попробуйте еще раз. {er}')
    except Exception as er:
        if ans == None:
            await message.answer(f"Слишком частые запросы, подождите 20 секунд.->{er}")
        else:
            try:
                gpt = AsyncGPT(str(message.from_user.id))
                gpt.deleteTokens()
                ans = await gpt.tell(message.text)
                await message.answer(ans)
                
            except:
                await message.answer(f'Извините, попробуйте еще раз. {er}')

async def tell_private(message: types.Message, count = 0):
    ans = None
    try:
        await bot.send_chat_action(message.chat.id, types.ChatActions.TYPING)
        gpt = AsyncGPT(str(message.from_user.id))
        ans = await gpt.tell(message.get_args())
        await message.answer(ans)
        try:
            await ad(message, message.from_user.id)
        except Exception as er:
            await message.answer(f'Извините, попробуйте еще раз. {er}')
    except Exception as er:
        if ans == None:
            await message.answer("Слишком частые запросы, подождите 20 секунд.")
        else:
            gpt = GPT(str(message.from_user.id))
            gpt.deleteTokens()
            
            if count > 3:
                await message.answer(f'Извините, попробуйте еще раз. {er}')
            else:
                await tell(message, count+1)

async def tell_public(message: types.Message, count = 0):
    ans = None
    try:
        if message.chat.type == 'private':
            await message.answer("Извините, эта функция не доступна в личных сообщениях с ботом.")
            return
        
        await bot.send_chat_action(message.chat.id, types.ChatActions.TYPING)
        gpt = AsyncGPT(str(message.chat.id))
        ans = await gpt.tell(message.text)
        await message.answer(ans)
        try:
            await ad(message, message.from_user.id)
        except Exception as er:
            await message.answer(f'Извините, попробуйте еще раз. {er}')
    except Exception as er:
        if ans == None:
            await message.answer("Слишком частые запросы, подождите 20 секунд.")
        else:
            gpt = GPT(str(message.from_user.id))
            gpt.deleteTokens()
            
            if count > 3:
                await message.answer(f'Извините, попробуйте еще раз. {er}')
            else:
                await tell(message, count+1)

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
    s6 = "/image - сгенирировать картинку\n"
    s7 = "Пример: /image сгенирируй фото котика\n"
    s8 = "/tell - отправка сообщения боту не от конкретного пользователя, а от чата (работает только в групповых чатах)\n"
    s9 = "/ls - отправка сообщения боту от конкретного пользователя (в лс с ботом можно не указывать)"

    await message.answer(s1+s2+s3+s4+s5+s6+s7+s8+s9)

async def reset(message: types.Message):
    s = """
        Здравствуйте! Чем могу помочь?
    """
    GPT(str(message.from_user.id)).reset()
    await message.answer(s)

async def reset_public(message: types.Message):
    if message.chat.type == 'private':
        await message.answer("Извините, эта функция не доступна в личных сообщениях с ботом.")
        return
    
    s = """
        Здравствуйте! Чем могу помочь?
    """
    GPT(str(message.chat.id)).reset()
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

async def get_image(message: types.Message):
    text = message.get_args()
    gpt = AsyncGPT(str(message.from_user.id))

    msg = await message.answer('Обрабатывается... ⌛️')
    image_src = await gpt.try_DALLE(text)
    print('IMAGE', image_src)
    if type(image_src) != str:
        r = str(image_src[1]['message'])
        await msg.delete()
        await message.answer(f"<i>{r}</i>", parse_mode="HTML")
        await ad(message, message.from_user.id)
        return
    image = await download_http(image_src)
    await message.answer_photo(image)
    await msg.delete()
    await ad(message, message.from_user.id)

async def get_image_stable(message: types.Message):
    text = message.get_args()
    gpt = AsyncGPT(str(message.from_user.id))

    msg = await message.answer('Обрабатывается... ⌛️')
    image_src = await gpt.try_Diffusion(text)
    print('IMAGE', image_src)
    if type(image_src) != str:
        r = str(image_src[1]['message'])
        await msg.delete()
        await message.answer(f"<i>{r}</i>", parse_mode="HTML")
        await ad(message, message.from_user.id)
        return
    image = await download_http(image_src)
    await message.answer_photo(image)
    await msg.delete()
    await ad(message, message.from_user.id)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands = ['start'])
    dp.register_message_handler(help, commands = ['help'])
    dp.register_message_handler(reset, commands = ['reset'])
    dp.register_message_handler(reset_public, commands = ['reset_public'])
    dp.register_message_handler(edit_key, commands = ['login'])
    dp.register_message_handler(tell_public, commands = ['tell'])
    dp.register_message_handler(tell_private, commands = ['ls'])
    dp.register_message_handler(get_image, commands = ['image'])
    dp.register_message_handler(get_image_stable, commands = ['image_stable'])
    dp.register_message_handler(tell)
