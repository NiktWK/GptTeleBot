from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types.bot_command import BotCommand
from aiogram.dispatcher import FSMContext
from states.states import *
import aiohttp, asyncio, config
from for_data.ad import *
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.exceptions import ChatNotFound
from keyboards.keyboards import goal_audit_kb, yes_no_kb, empty_kb
from _pyio import BufferedReader

bot = Bot("5971945403:AAHh_JwUkuIG1L_pAd8pNLMtOlIdHJHW07Y")
dp = Dispatcher(bot, storage = MemoryStorage())

#START_AD = Ad(0, empty = True)
IMAGE_DIR = config.IMAGE_PATH


# Base functions
async def set_commands(bot : Bot):
    commands = [
        BotCommand('/start', 'Начать'),
        BotCommand('/help', 'Помощь')
    ]
    await bot.set_my_commands(commands)

# Check is admin
async def verify(id):
    with open(f'{config.USERS_DATA_PATH}admin.json', 'r') as file:
        admins = json.load(file)

        if id in admins:

            print(id, admins)
            return True
        
    return False

# Other functions
async def get_users_info(message: types.Message):
    if not(await verify(message.from_user.id)):
        await message.answer('У вас нет разрешения на доступ.')
        return
    
    try:
        with open(f'{config.USERS_DATA_PATH}user.json', 'r') as file:
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
        with open(f'{config.AD_PATH}ads.json', 'r', encoding='utf-8') as ads_file:
            await message.answer(str(json.load(ads_file)))
        
    except Exception as er:
        await message.answer(f'Error {er}')
    
async def delete_old_ads(message: types.Message):
    if not(await verify(message.from_user.id)):
        await message.answer('У вас нет разрешения на доступ.')
        return
    
    try:
        with open(f'{config.AD_PATH}ads.json', 'r', encoding='utf-8') as ads_file:
            ads = json.load(ads_file)
            newads = dict()
            count = 0
            for key in ads:
                if ads[key]['count'] <= ads[key]['max-shows']:
                    newads[str(count)] = ads[key]
                    count+=1
        
        with open(f'{config.AD_PATH}ads.json', 'w', encoding='utf-8') as ads_file:
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
    s7 = "/getadsinfo - информация о рекламе\n"
    s8 = "/mailing - рассылка"
    await message.answer(s1+s2+s3+s4+s5+s6+s7+s8)

async def save_users(message: types.Message, path):
    if not(await verify(message.from_user.id)):
        await message.answer('У вас нет разрешения на доступ.')
        return
    
    with open(path, 'w', encoding='utf-8') as file:
        data = json.load(file)

    with open('{}{}'.format(config.SAVED_DATA_PATH, path.split('/')[-1]), 'w', encoding='utf-8') as file:
        json.dump(data, file)

    await message.answer('Успешно! Users')

async def save_users(message: types.Message, path):
    if not(await verify(message.from_user.id)):
        await message.answer('У вас нет разрешения на доступ.')
        return
    
    with open(path, 'w', encoding='utf-8') as file:
        data = json.load(file)

    with open('{}{}'.format(config.SAVED_DATA_PATH, path.split('/')[-1]), 'w', encoding='utf-8') as file:
        json.dump(data, file)

    await message.answer('Успешно! Users')
    
# # Add
# async def newad(message: types.Message, state: FSMContext):
#     if not(await verify(message.from_user.id)):
#         await message.answer('У вас нет разрешения на доступ.')
#         return
#     dump_ad(-1, START_AD, new = True)
#     await message.answer('Введите заголовок')
#     await state.set_state(NewAd.header)

# async def getHeader(message: types.Message, state: FSMContext):
#     try:
#         ad = Ad(-1, 'new')
#         ad.header = message.text
#         dump_ad(-1, ad)
#         await message.answer('Введите текст')
#         await state.set_state(NewAd.text)
#     except Exception as er:
#         await message.answer(f'Ошибка. Попробуйте еще раз. {er}')

# async def getText(message: types.Message, state: FSMContext):
#     try:
#         ad = Ad(-1, 'new')
#         ad.text = message.text
#         dump_ad(-1, ad)
#         await message.answer('Введите изображение. Если реклама без изображение - напишите "None"')
#         await state.set_state(NewAd.image)
#     except Exception as er:
#         await message.answer(f'Ошибка. Попробуйте еще раз. {er}')

async def downloadImage(message: types.Message):
    file_info = await bot.get_file(message.photo[-1].file_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    src = IMAGE_DIR + 'image' + message.photo[-1].file_id

    with open(src, 'wb') as new_image_file:
        new_image_file.write(downloaded_file.read())

    await message.answer('Фото успешно скачано!')

    return src

# async def getImage(message: types.Message, state: FSMContext):
#     image_path = None
#     if not message.photo:
#         await message.answer('Без изображения')
#     else:
#         image_path = await downloadImage(message)

#     await state.set_state(NewAd.shows)
#     await message.answer('Введите кол-во показов рекламы')
#     await state.update_data(img_path = image_path)

# async def getMaxShoows(message: types.Message, state: FSMContext):
#     try:
#         data = await state.get_data()
#         ad = Ad(-1, 'new')
#         ad.max_shows = int(message.text)
#         ad.image_path = data['img_path']
#         dump_ad(-1, ad)
#         replace_ad(-1, ad)
#         await state.finish()
#         await message.answer('Успешно!')
#     except Exception as er:
#         await message.answer(f'Ошибка. Попробуйте еще раз. {er}')

# Edit keys
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
    with open(config.KEYS_PATH + 'key_stable.bin', 'w') as kfile:
        kfile.write(message.text)
    await message.answer('Успешно!')
    await state.finish()

async def editOpenAI(message: types.Message, state: FSMContext):
    with open(config.KEYS_PATH + 'key_ai.bin', 'w') as kfile:
        kfile.write(message.text)
    await message.answer('Успешно!')
    await state.finish()

# Mailing
async def go_mailing(text, image_path, bot = bot, reply_markup = None, parse_mode = None, in_chats = False, in_users = False):

    missed_chats = []
    try:
        chats = await get_chats(in_chats, in_users)
        
        if image_path is None:
            for chat_id in chats:
                try:
                    await bot.send_message(chat_id, text, parse_mode, reply_markup=reply_markup)
                except ChatNotFound:
                    missed_chats.append(chat_id)
                    
        else:
            for chat_id in chats:

                try:
                    with open(image_path, 'rb') as image:
                        await bot.send_photo(chat_id, image, text, parse_mode, reply_markup=reply_markup)
                except ChatNotFound:
                    missed_chats.append(chat_id)

    except Exception as er:
        return (False, missed_chats, er)

    return (True, missed_chats, None)

async def mailing(message: types.Message, state: FSMContext):
    await message.answer('Введите текст рассылки')
    await state.set_state(Mailing.text)

async def mailing_text(message: types.Message, state: FSMContext):
    await message.answer('Пришлите картинку для рассылки. Если картинки нет - напишите любое слово')
    await state.update_data(text = message.text)
    await state.set_state(Mailing.image)

async def mailing_image(message: types.Message, state: FSMContext):
    await state.update_data(image_path = await downloadImage(message))
    await message.answer('Куда отправить?', reply_markup=goal_audit_kb)
    await state.set_state(Mailing.goal_auditory)

async def mailing_without_image(message: types.Message, state: FSMContext):
    await state.update_data(image_path = None)
    await message.answer('Куда отправить?', reply_markup=goal_audit_kb)
    await state.set_state(Mailing.goal_auditory)

async def mailing_goal_auditory(cq: types.CallbackQuery, state: FSMContext):
    goal_auditory = cq.data
    data = await state.get_data()
    text = data['text']
    image_path = data['image_path']
    chat_id = cq.message.chat.id
    await bot.send_message(chat_id, 'Вот что получилось:', parse_mode='Markdown')
    if image_path is None:
        await bot.send_message(chat_id, text, parse_mode='Markdown')
    else:
        with open(image_path, 'rb') as image:
            await bot.send_photo(chat_id, image, text, parse_mode='Markdown')

    await cq.message.edit_reply_markup(empty_kb)
    await bot.send_message(chat_id, 'Все верно?', parse_mode='Markdown', reply_markup=yes_no_kb)
    await state.update_data(goal_auditory = cq.data)
    await state.set_state(Mailing.check_result)

async def mailing_check_result(cq: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if cq.data == 'yes':
        to_json = {
            'image_path': data['image_path'],
            'text': data['text'],
            'goal_auditory': data['goal_auditory']
        }

        # запускаем рассылку
        with open(config.MAILING_PATH + 'mailing.json', 'w', encoding='utf-8') as file:
            json.dump(to_json, file, ensure_ascii=False, indent=4) 

        await bot.send_message(cq.message.chat.id, 'Готово, можете начинать')
    else:
        image_path = data['image_path']
        if image_path is not None:
            os.remove(image_path)

        await state.finish()
        await bot.send_message(cq.message.chat.id, 'Отменено')

# AD
async def ad(message: types.Message, state: FSMContext):
    await message.answer('Введите текст рекламы')
    await state.set_state(Mailing.text)

async def ad_text(message: types.Message, state: FSMContext):
    await message.answer('Пришлите картинку для рекламы. Если картинки нет - напишите любое слово')
    await state.update_data(text = message.text)
    await state.set_state(AD.image)

async def ad_image(message: types.Message, state: FSMContext):
    await state.update_data(image_path = await downloadImage(message))
    await message.answer('Сколько показов?')
    await state.set_state(AD.max_shows)

async def ad_without_image(message: types.Message, state: FSMContext):
    await state.update_data(image_path = None)
    await message.answer('Сколько показов?')
    await state.set_state(AD.max_shows)

async def ad_max_shows(message: types.Message, state: FSMContext):
    max_shows = message.text

    try:
        int(max_shows)
    except:
        await bot.send_message(chat_id, '*Ошибка!* Введенные данные не являются целым числом!', parse_mode='Markdown')
        return
    
    data = await state.get_data()
    text = data['text']
    image_path = data['image_path']

    chat_id = message.chat.id
    await bot.send_message(chat_id, 'Вот что получилось:', parse_mode='Markdown')

    if image_path is None:
        await bot.send_message(chat_id, text, parse_mode='HTML')
    else:
        with open(image_path, 'rb') as image:
            await bot.send_photo(chat_id, image, text, parse_mode='HTML')

    await bot.send_message(chat_id, '*Количество показов: {}*'.format(max_shows), parse_mode='Markdown')
                           
    await bot.send_message(chat_id, 'Все верно?', parse_mode='Markdown', reply_markup=yes_no_kb)
    await state.update_data(max_shows = int(max_shows))
    await state.set_state(AD.check_result)

async def ad_check_result(cq: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if cq.data == 'yes':
        to_json = {
            'image-path': data['image_path'],
            'text': data['text'],
            'shows': 0,
            'max-shows': data['max_shows']
        }
        # сохраняем рекламу

        Ad(0, True).save(to_json)
        await bot.send_message(cq.message.chat.id, 'Готово')
        await state.finish()
    else:
        image_path = data['image_path']
        if image_path is not None:
            os.remove(image_path)

        await state.finish()
        await bot.send_message(cq.message.chat.id, 'Отменено')


async def All(message: types.Message, state: FSMContext):
    await message.answer('...')

def register_handlers(dp : Dispatcher):
    dp.register_message_handler(help, commands=['help'])
    dp.register_message_handler(editkey, commands=['editkey'])
    dp.register_message_handler(get_users_info, commands=['getusersinfo'])
    dp.register_message_handler(get_ads_info, commands=['getadsinfo'])
    dp.register_message_handler(delete_old_ads, commands=['deletead'])

    ## handlers for a AD
    dp.register_message_handler(ad, commands=['newad'])
    dp.register_message_handler(ad_text, state = AD.text)
    dp.register_message_handler(ad_image, state = AD.image, content_types=[types.ContentType.PHOTO])
    dp.register_message_handler(ad_without_image, state = AD.image, content_types=[types.ContentType.TEXT])
    dp.register_message_handler(ad_max_shows, state = AD.max_shows)
    dp.register_callback_query_handler(ad_check_result, state = AD.check_result)

    # handlers for editing a keys
    dp.register_message_handler(change_key_type, state = EditKey.change_type)
    dp.register_message_handler(editStableDiffusion, state = EditKey.edit_diffusion)
    dp.register_message_handler(editOpenAI, state = EditKey.edit_openai)

    # handlers for a mailing
    dp.register_message_handler(mailing, commands=['mailing'])
    dp.register_message_handler(mailing_text, state = Mailing.text)
    dp.register_message_handler(mailing_image, state = Mailing.image, content_types=[types.ContentType.PHOTO])
    dp.register_message_handler(mailing_without_image, state = Mailing.image, content_types=[types.ContentType.TEXT])
    dp.register_callback_query_handler(mailing_goal_auditory, state = Mailing.goal_auditory)
    dp.register_callback_query_handler(mailing_check_result, state = Mailing.check_result)

    # handlers for other messages
    dp.register_message_handler(All)

# Main
async def main():
    global bot, dp
    register_handlers(dp)  
    await set_commands(bot)
    await dp.start_polling()
    aiohttp.ClientSession().close()
    
if __name__ == '__main__':
    asyncio.run(main())