from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types.bot_command import BotCommand
from aiogram.dispatcher import FSMContext
from states import *
import aiohttp, asyncio
from ad import *
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton

bot = Bot("5971945403:AAHh_JwUkuIG1L_pAd8pNLMtOlIdHJHW07Y")
dp = Dispatcher(bot, storage = MemoryStorage())

START_AD = Ad(0, empty = True)
IMAGE_DIR = 'data/image/'

async def set_commands(bot : Bot):
    commands = [
        BotCommand('/start', 'Начать'),
        BotCommand('/help', 'Помощь')
    ]
    await bot.set_my_commands(commands)

async def verify(id):
    with open('admin.json', 'r') as file:
        admins = json.load(file)

        if str(id) in admins:
            return True
        
    return False

async def get_users_info(message: types.Message):
    if not(await verify(message.from_user.id)):
        await message.answer('У вас нет разрешения на доступ.')
        return
    
    try:
        with open('user.json', 'r') as file:
            users = json.load(file)

            info = {}

            info['users-quantity'] = len(users)

            always_users = []
            always_q = -1
            for user in users:
                if len(users[user]['messages']) == always_q:
                    always_users.append(user)
                if len(users[user]['messages']) > always_q:
                    always_users = []
                    always_users.append(user)
                    always_q = users[user]['count']

            
            info['always-users'] = {'users': always_users, 'quantity': always_q}

            await message.answer(str(info))
        
    except Exception as er:
        await message.answer(f'Error {er}')

async def get_ads_info(message: types.Message):
    if not(await verify(message.from_user.id)):
        await message.answer('У вас нет разрешения на доступ.')
        return

    try:
        with open('data/ads.json', 'r', encoding='utf-8') as ads_file:
            await message.answer(str(json.load(ads_file)))
        
    except Exception as er:
        await message.answer(f'Error {er}')
    
async def delete_old_ads(message: types.Message):
    if not(await verify(message.from_user.id)):
        await message.answer('У вас нет разрешения на доступ.')
        return
    
    try:
        with open('data/ads.json', 'r', encoding='utf-8') as ads_file:
            ads = json.load(ads_file)
            newads = dict()
            count = 0
            for key in ads:
                if ads[key]['count'] <= ads[key]['max-shows']:
                    newads[str(count)] = ads[key]
                    count+=1
        
        with open('data/ads.json', 'w', encoding='utf-8') as ads_file:
            json.dump(newads, ads_file, ensure_ascii=False, indent=4)

        await message.answer('Success')
    
    except Exception as er:
        await message.answer(f'Error {er}')
    
async def help(message: types.Message):
    s1 = "Чтобы начать общение с ботом - напишите любую фразу.\n"
    s2 = "/newad - добавить рекламу\n"
    s3 = "/editad - изменить рекламу\n"
    s4 = "/deletead - удалить рекламу\n"
    s5 = "/editkey - изменить GPT-токен\n"
    s6 = "/getusersinfo - информация о пользователях\n"
    s7 = "/getadsinfo - информация о рекламе"
    await message.answer(s1+s2+s3+s4+s5+s6+s7)


async def newad(message: types.Message, state: FSMContext):
    if not(await verify(message.from_user.id)):
        await message.answer('У вас нет разрешения на доступ.')
        return
    dump_ad(-1, START_AD, new = True)
    await message.answer('Введите заголовок')
    await state.set_state(NewAd.header)

async def getHeader(message: types.Message, state: FSMContext):
    try:
        ad = Ad(-1, 'new')
        ad.header = message.text
        dump_ad(-1, ad)
        await message.answer('Введите текст')
        await state.set_state(NewAd.text)
    except Exception as er:
        await message.answer(f'Ошибка. Попробуйте еще раз. {er}')

async def getText(message: types.Message, state: FSMContext):
    try:
        ad = Ad(-1, 'new')
        ad.text = message.text
        dump_ad(-1, ad)
        await message.answer('Введите изображение. Если реклама без изображение - напишите "None"')
        await state.set_state(NewAd.image)
    except Exception as er:
        await message.answer(f'Ошибка. Попробуйте еще раз. {er}')

async def downloadImage(message: types.Message):
    file_info = await bot.get_file(message.photo[-1].file_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    src = IMAGE_DIR + 'image' + message.photo[1].file_id

    with open(src, 'wb') as new_image_file:
        new_image_file.write(downloaded_file)

    message.answer('Фото успешно скачано!')

    return src

async def getImage(message: types.Message, state: FSMContext):

    if message.text != "":
        await message.answer('Без изображения')
    else:
        image_path = await downloadImage(message)
        ad = Ad(-1, 'new')
        ad.image_path = image_path
        dump_ad(-1, ad)
    await state.set_state(NewAd.shows)
    await message.answer('Введите кол-во показов рекламы')

async def getMaxShoows(message: types.Message, state: FSMContext):
    try:
        ad = Ad(-1, 'new')
        ad.max_shows = int(message.text)
        ad.count = 0
        dump_ad(-1, ad)
        replace_ad(-1, ad)
        await state.finish()
        await message.answer('Успешно!')
    except Exception as er:
        await message.answer(f'Ошибка. Попробуйте еще раз. {er}')


async def editkey(message: types.Message, state: FSMContext):
    if not(await verify(message.from_user.id)):
        await message.answer('У вас нет разрешения на доступ.')
        return
    button_openai = KeyboardButton('OpenAI')
    button_diffusion = KeyboardButton('Stable Diffusion')
    types_buttons = ReplyKeyboardMarkup()
    types_buttons.add(button_openai, button_diffusion)

    await message.answer('Выберите тип:', reply_markup = types_buttons)
    await state.set_state(EditKey.change_type)

async def change_key_type(message: types.Message, state: FSMContext):
    if message.text == 'OpenAI':
        await message.answer('Введите ключ для OpenAI')
        await state.set_state(EditKey.edit_openai)
    elif message.text == 'Stable Diffusion':
        await message.answer('Введите ключ для StableDiffusion')
        await state.set_state(EditKey.edit_diffusion)
    else:
        await message.answer('Неверное значение')
        await state.finish()

async def editStableDiffusion(message: types.Message, state: FSMContext):
    with open('key_stable.bin', 'w') as kfile:
        kfile.write(message.text)
    await message.answer('Успешно!')
    await state.finish()

async def editOpenAI(message: types.Message, state: FSMContext):
    with open('key_openai', 'w') as kfile:
        kfile.write(message.text)
    await message.answer('Успешно!')
    await state.finish()


async def All(message: types.Message, state: FSMContext):
    print("all")
    await message.answer('...')

def register_handlers(dp : Dispatcher):
    dp.register_message_handler(help, commands=['help'])
    dp.register_message_handler(newad, commands=['newad'])
    dp.register_message_handler(editkey, commands=['editkey'])
    dp.register_message_handler(get_users_info, commands=['getusersinfo'])
    dp.register_message_handler(get_ads_info, commands=['getadsinfo'])
    dp.register_message_handler(delete_old_ads, commands=['deletead'])
    dp.register_message_handler(getHeader, state = NewAd.header)
    dp.register_message_handler(getText, state = NewAd.text)
    dp.register_message_handler(getImage, state = NewAd.image)
    dp.register_message_handler(getMaxShoows, state = NewAd.shows)
    dp.register_message_handler(change_key_type, state = EditKey.change_type)
    dp.register_message_handler(editStableDiffusion, state = EditKey.edit_diffusion)
    dp.register_message_handler(editOpenAI, state = EditKey.edit_openai)

    
    dp.register_message_handler(All)

async def main():
    global bot, dp
    register_handlers(dp)  
    await set_commands(bot)
    await dp.start_polling()
    aiohttp.ClientSession().close()
    
if __name__ == '__main__':
    asyncio.run(main())