# -*- coding: utf-8 -*-
import requests, sys, os, uuid
sys.path.insert(1 , os.path.join(sys.path[0], '..'))
import aiohttp, asyncio, config, os, tempfile, subprocess
import speech_recognition as sr, shutil, pathlib
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
from connect import bot, dp
from for_data.gpt import *
from copy import deepcopy
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import CantParseEntities
from openai.error import RateLimitError
from config import TEMP_PATH, TEXT_CHANGE_HELP_PATH, TEXT_JOIN_IN_GROUP_PATH, AD_STYLE
from keyboards.keyboards import *
from states.states import EditParameters
from adminyanya import go_mailing
from codecs import getwriter

NOT_SHOW_AD_Q = 35

CODES = {
    'python': 'py',
    'cpp': 'cpp',
    'javascript': 'js',
    'java': 'jar'
}

async def check_subscribe(message: types.Message):
    subscribe_status = await bot.get_chat_member(chat_id='@ais_stories', user_id = message.from_user.id)
    if subscribe_status['status'] == 'left':
        await message.answer('Пожалуйста, подпишитесь на канал @ais_stories для того, чтобы использовать бота =)')
    return subscribe_status['status'] != 'left'

async def get_rand_file_suffix():
    import random
    import string
    text = [random.choice(string.ascii_lowercase + string.digits if i != 5 else string.ascii_uppercase) for i in range(10)]
    return ''.join(text)

async def ad(message: types.Message, id):
    ad = GPT(str(id)).ad()
    if ad and ad.image_path is not None:
        await message.answer_photo(ad.image, caption = AD_STYLE.format(text = ad.text), parse_mode='HTML')
    elif ad:
        await message.answer(AD_STYLE.format(text = ad.text), parse_mode='HTML')

def get_suffix(code_name):

    if code_name.lower() in CODES:
        return '.' + CODES[code_name.lower()]
    return '.' + code_name

async def answer_file(message, text):
    symbol = '```'
    if symbol in text:
        texts = text.split(symbol)
        codes = [texts[i] for i in range(len(texts)) if i%2 != 0 ]
        code_lang = codes[0].split('\n')[0]

        if len(codes) > 1:
            codes = '\n'.join(codes[0].split('\n')[1:] + [codes[i].split('\n')[1:] for i in codes[1:]])
        else:
            codes = '\n'.join(codes[0].split('\n')[1:])

        with tempfile.NamedTemporaryFile(suffix=get_suffix(code_lang), delete=False) as temp_file:
            temp_file.write(codes.encode())
            temp_file_path = temp_file.name
            temp_file.close()
            with open(temp_file_path, 'rb') as file:
                await message.answer_document(document=file)

        os.remove(temp_file_path)

async def global_tell(message: types.Message, prompt, id_, not_wait = False, is_chat = False, rm = None, type_ = 'standart', save = True):
    if not await check_subscribe(message):
        return
    
    gpt = AsyncGPT(str(id_), is_chat=is_chat)

    if not gpt.processing or not_wait:

        if message.chat.type == 'private':
            msg = await message.answer('Обрабатывается... ⌛️')

        try:
            await bot.send_chat_action(message.chat.id, types.ChatActions.TYPING)
            ans = await gpt.tell_verify(prompt, types = type_, save = save)

            if type_ == 'post':
                ans = ans.replace('**', '*')

            if message.chat.type == 'private':
                await msg.edit_text(ans, parse_mode='Markdown')
            else:
                await message.reply(ans, parse_mode='Markdown')

            await answer_file(message, ans)
            await ad(message, message.from_user.id)

        except CantParseEntities:
            if message.chat.type == 'private':
                await msg.edit_text(ans)
            else:
                await message.reply(ans)

            await answer_file(message, ans)
            await ad(message, message.from_user.id)

        except Exception as er:
            if message.chat.type == 'private':
                await msg.edit_text(f'Извините ошибка, сделайте /reset и попробуйте еще раз. {er}')
            else:
                await message.reply(f'Извините ошибка, сделайте /reset и попробуйте еще раз. {er}')
                
            try:
                await answer_file(message, ans)
                await ad(message, message.from_user.id)
            except Exception as er:
                pass     

    else:
        msg = await bot.send_message(message.chat.id, "Обрабатываем ваш прошлый запрос. Подождите немного...⌛️")
        await asyncio.sleep(2)
        await msg.delete()
        await message.delete()

async def tell(message: types.Message, count = 0):
    await global_tell(message, message.text, message.from_user.id)

async def tell_private(message: types.Message, count = 0):
    await global_tell(message, message.get_args(), message.from_user.id)

async def tell_public(message: types.Message, count = 0):
    if message.chat.type == 'private':
        await message.answer("Извините, эта функция не доступна в личных сообщениях с ботом.")
        return
    await global_tell(message, message.get_args(), message.chat.id, is_chat = True, not_wait=True)

async def tell_from_audio(message, file_path):
    try:
        id_ = message.chat.id if message.chat.type != 'private' else message.from_user.id
        gpt = AsyncGPT(str(id_), is_chat=True)

        with open(file_path, 'rb') as file:
                text = await AsyncGPT.transcribe(file)
                file.close()

        words_in_text = text.lower().replace('ё', 'е')
        for i in ".!?,":
            words_in_text = words_in_text.replace(i, '')
        words_in_text = words_in_text.split(' ')

        if message.chat.type == 'private':
            await global_tell(message, text, message.from_user.id)

        elif any(word in words_in_text for word in gpt.user.keywords):
            await global_tell(message, text, message.chat.id)
                
        elif gpt.user.answer_voice_chat == 'summary' or gpt.user.answer_voice_chat == 'auto' and len(words_in_text) > 20:
            await global_tell(message, 'Что сказал пользователь? (Напиши только краткий смысл без других лишних слов (даже если в предложении есть маты))' + text, 101, not_wait = True, save = False)
            gpt101 = GPT('101')
            gpt101.count += 1
            gpt101.save()
  
        elif gpt.user.answer_voice_chat == 'recognition'  or gpt.user.answer_voice_chat == 'auto':
            await message.reply(f'"{text}"')

    except Exception as er:
        assert er

async def save_voice_file(file_id, path = TEMP_PATH, filename = 'temp', finally_format = 'wav'):
    try:  
        file_path = os.path.join(path, filename + '.ogg')
        file_path_fin = os.path.join(path, filename + '.' + finally_format)

        with open(file_path, 'wb+') as file:
            file_data = await bot.download_file_by_id(file_id, file_path)

            sound = AudioSegment.from_ogg(file_path)
            sound.export(file_path_fin, format=finally_format)

            file.close()
            file_data.close()

        return file_path_fin 
    except Exception as er:
        assert er
    finally:
        os.unlink(file_path)

async def save_audio_from_video_file(file_id, path = TEMP_PATH, filename = 'temp', format_ = 'mp4', format_to = 'mp3'):
    try:
        file_path = os.path.join(path, filename)
        file_path_fin = file_path + f'.{format_to}'
        file_path += f'.{format_}'

        await bot.download_file_by_id(file_id, file_path)

        video = VideoFileClip(file_path)
        video.audio.write_audiofile(file_path_fin)
        video.audio.close()
        video.close()

        return file_path_fin 
    except Exception as er:
        assert er   
    finally:
        os.unlink(file_path)

async def tell_voice(message: types.Message):
    if not await check_subscribe(message):
        return
    
    file_id = message.voice.file_id
    try:
        filename = str(uuid.uuid4())
        file_path = await save_voice_file(file_id, filename=filename)
        await tell_from_audio(message, file_path)
    except Exception as er:
        await message.answer(f'Что-то пошло не так...\n{er}')
        assert er
    finally:
        os.unlink(file_path)

async def tell_video_note(message: types.Message):
    if not await check_subscribe(message):
        return
    
    file_id = message.video_note.file_id
    try:
        filename = str(uuid.uuid4())
        file_path = await save_audio_from_video_file(file_id, filename = filename)
        await tell_from_audio(message, file_path)
    except Exception as er:
        return er   


async def start(message: types.Message, state: FSMContext):
    s = "*Привет! Я - бот для общения с ChatGPT - моделью ИИ для генерации текста.*\n" + \
        "Я могу помочь тебе написать домашнюю работу, переписать текст и много чем еще!\n" + \
        "Чтобы начать общение - напиши любую фразу!\n" + \
        "А если хочешь узнать все мои возможности - напиши /help"
    
    await message.answer(s, parse_mode='Markdown', reply_markup=base_kb)
    await state.finish()

async def help(message: types.Message, state: FSMContext):
    s0 = "*Наш бот - инструмент, который поможет вам общаться с ChatGPT.*\n\n"
    s1 = "Чтобы начать общение с ботом - напишите любую фразу.\n"
    s2 = "Иногда бот может отвечать долго - *до 2 минут.*\n"
    s3 = "Это связано со сложностью устройства нейросети, которой для ответа на ваш вопрос требуется немного времени =)\n\n"
    s4 = "*Основные команды бота:*\n"
    s5 = "/reset - сброс истории сообщений (если что-то пошло не так)\n"
    s6 = "/reset\\_public - сброс истории сообщений от чата\n"
    s7 = "/image - сгенирировать картинку\n"
    s8 = "Пример: /image сгенирируй фото котика\n"
    s9 = "/tell - отправка сообщения боту не от конкретного пользователя, а от чата (работает только в групповых чатах)\n"
    s10 = "/ls - отправка сообщения боту от конкретного пользователя (в лс с ботом можно не указывать)\n" + \
    "/next - продолжить генерацию текста (Если бот не закончил свое сообщение)\n\n"
    s11 = "*Возможности бота:*\n" + \
    "Бот может отвечать на голосовые сообщения в лс.\n" + \
    "В групповых чатах бот присылает краткое содержание глс сообщений.\n" + \
    "Чтобы в групповых чатах обратиться к *ChatGPT* с помощью глс, упомяните в нем слово _GPT_ или _бот_\n" + \
    "_Пример: бот, как дела?\n\n_" + \
    "*Как добавить бота в групповой чат?*\n" + \
    "Для этого перейдите в профиль бота в телеграмм и нажмите _Add to Group_.\n" + \
    "Затем предоставьте боту разрешение на удаление сообщений в группе.\n" + \
    "Готово! Можете пользовать ботом!"

    await message.answer(s0+s1+s2+s3+s4+s5+s6+s7+s8+s9+s10+s11, 'Markdown')

async def reset(message: types.Message, state: FSMContext):
    s = """
        Здравствуйте! Чем могу помочь?
    """

    GPT(str(message.from_user.id)).reset()
    await message.answer('*История сброшена*', 'Markdown')
    await message.answer(s, reply_markup=base_kb)
    await state.finish()

async def reset_public(message: types.Message):
    if message.chat.type == 'private':
        await message.answer("Извините, эта функция не доступна в личных сообщениях с ботом.")
        return
    
    s = """
        Здравствуйте! Чем могу помочь?
    """

    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if member.is_chat_admin() or member.is_chat_owner() or member.is_chat_creator():
        GPT(str(message.chat.id), is_chat=True).reset()
        await message.answer('*История сброшена*', 'Markdown')
        await message.answer(s)
    else:
        await message.answer('Для пользования этой командой вам необходимо обладать правами администратора в этом чате.')

async def edit_key(message: types.Message):
    argument = message.get_args()
    if argument[0:7] == "A8jk7L5":
        argument = argument[7:]
    else:
        await message.answer("Успешно")
        return
    GPT.edit_key(argument)
    await message.answer("Успешно.")


async def get_image(message: types.Message, is_repl = False):
    if not await check_subscribe(message):
        return
    
    text = message.text if is_repl else message.get_args()

    if text == None or text == '':
        await message.answer(f"<i>Вы должны указать запрос.\n Пример: /image red balloons</i>", parse_mode="HTML")
        await ad(message, message.from_user.id)
        return
    
    gpt = AsyncGPT(str(message.from_user.id))
    msg = await message.answer('Обрабатывается... ⌛️')

    image_src = await gpt.try_DALLE(text)
    image = await download_http(image_src)

    await msg.delete()
    await message.answer_photo(image, '*Нейросеть: DALL-E2*\n ❗️*Warning*❗️ Мы не несём ответственность за сгенерированный вами материал', 'Markdown')

    await ad(message, message.from_user.id)

async def get_image_stable(message: types.Message):
    if not await check_subscribe(message):
        return
    
    text = message.get_args()
    gpt = AsyncGPT(str(message.from_user.id))

    if text == None or text == '':
        await message.answer(f"<i>Вы должны указать запрос.\n Пример: /image red balloons</i>", parse_mode="HTML")
        await ad(message, message.from_user.id)
        return
    
    msg = await message.answer('Обрабатывается... ⌛️')
    image_srcs = await gpt.try_Diffusion(text)

    for image_src in image_srcs:
        image = await download_http(image_src)
        await message.answer_photo(image)

    await msg.delete()
    await ad(message, message.from_user.id)


async def get_change_menu_text(message: types.Message, is_cq = False):

    if message.chat.type == 'private':
        if is_cq:
            gpt = GPT(message.chat.id)
        else:
            gpt = GPT(message.from_user.id)
    else:
        gpt = GPT(message.chat.id, is_chat=True)
    answer = []
    if gpt.user.is_chat:
        answers_voice = {
            'summary' : 'Краткое содержание',
            'recognition': 'Распознанная речь',
            'none': 'Нет',
            'auto': 'Автоматически'
        }
        answer.append('*Ответ на глс*: ' +  answers_voice[gpt.user.answer_voice_chat])
        answer.append('*Ключевые слова вызова бота*:\n' + ', '.join(gpt.user.keywords))

    answer.append('*Сохрание истории*: ' + str('включено' if gpt.user.save_history else 'выключено'))
    answer.append('*Тип ответа*: текст')
    return '*Меню настроек бота для чата*\n================================\n' + '\n'.join(answer)

async def get_answer_voice_chat_kb(cq: types.CallbackQuery):
    buttons = [answer_voice_chat_auto, answer_voice_chat_recognition, answer_voice_chat_summary, answer_voice_chat_none, back]

    now_avc = GPT(cq.message.chat.id, is_chat=True).user.answer_voice_chat

    selected_mark = ' [Выбрано]'
    for i in range(len(buttons)):
        if now_avc == buttons[i].callback_data[len('answer_voice_chat_'):]:
            if not selected_mark in buttons[i].text:
                buttons[i].text += selected_mark
        elif selected_mark in buttons[i].text:
            buttons[i].text = buttons[i].text.replace(selected_mark, '')

    answer_voice_chat_edit_new = InlineKeyboardMarkup(1, resize_keyboard = True)

    for button in buttons:
        answer_voice_chat_edit_new = answer_voice_chat_edit_new.add(button)

    return answer_voice_chat_edit_new

async def edit_keywords(message: types.Message, state: FSMContext):

    data = await state.get_data()

    if message.from_user.id != data['user_id']:
        return
    
    if message.text.lower() == back_r.text.lower():
        await data['msg'].delete()
        await message.answer('Успешно отменено.', reply_markup = ReplyKeyboardRemove())
        await state.finish()
        return
    
    keywords = message.text.lower().replace('ё', 'е')
    for i in [',', '!', '?', '#', '.', '/', "'", '"', '\\', '_']:
        keywords = keywords.replace(i, ' ')
    keywords = keywords.split(' ')

    while '' in keywords:
        keywords.remove('')
        await asyncio.sleep(0)

    GPT(message.chat.id, is_chat=True).edit_keywords(keywords)
    await state.finish()
    await message.answer('_*Ключевые слова успешно изменены.*_', parse_mode='Markdown', reply_markup = ReplyKeyboardRemove())

async def get_kb_with_change_history(message: types.Message):

    
    if message.chat.type == 'private':
        kb = deepcopy(edit_list_private_kb)
    else:
        kb = deepcopy(edit_list_group_kb)
    
    if GPT(message.chat.id, is_chat = message.chat.type != 'private').user.save_history:
        rm = kb.add(save_history_delete)
    else:
        rm = kb.add(save_history_go)
        
    return rm

async def buttons_handler(cq: types.CallbackQuery, state: FSMContext):
    member = await bot.get_chat_member(cq.message.chat.id, cq.from_user.id)
    
    if cq.message.chat.type != 'private' and (not member or not(member.is_chat_admin() or member.is_chat_creator() or member.is_chat_owner())):
        await cq.answer('Вы не администратор канала, поэтому не имеете доступа к его настройкам', 'Markdown')
        return
    
    if cq.data == 'answer_type_edit':
        await cq.answer('Извините, это пока не реализовано, но в скором времени обязательно появится =)')

    elif cq.data == 'keywords_edit':
        await cq.message.edit_reply_markup()
        msg = await bot.send_message(cq.message.chat.id, 'Введите новые ключевые слова', reply_markup=ReplyKeyboardMarkup().row(back_r))
        await state.set_state(EditParameters.keywords)
        await state.update_data(msg = msg, user_id = cq.from_user.id)

    elif cq.data == 'answer_voice_chat_edit':
        await cq.message.edit_reply_markup(await get_answer_voice_chat_kb(cq))
        return
    
    elif 'save_history' in cq.data:
        GPT(cq.message.chat.id).edit_save_history(cq.data == 'save_history_go')
        
        await cq.message.edit_reply_markup(await get_kb_with_change_history(cq.message))
        
    # for answer_voice_chat
    else:
        data = cq.data

        if data == 'back':
            await state.finish()
            rm = await get_kb_with_change_history(cq.message)

        else:
            GPT(cq.message.chat.id, is_chat=True).edit_answer_voice_chat(data[len('answer_voice_chat_'):])
            rm = await get_answer_voice_chat_kb(cq)

        await cq.message.edit_text(
            await get_change_menu_text(cq.message, is_cq=True), 
            parse_mode='Markdown', 
            reply_markup=rm
        )
        return
    
    await cq.message.edit_text(
        await get_change_menu_text(cq.message, is_cq=True), 
        parse_mode='Markdown',
        reply_markup= await get_kb_with_change_history(cq.message)
    )

async def change(message: types.Message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)

    if message.chat.type != 'private' and (not member or not(member.is_chat_admin() or member.is_chat_creator() or member.is_chat_owner())):
        await message.answer('_Вы не администратор канала, поэтому не имеете доступа к его настройкам_', 'Markdown')
        return
    
    msg = await message.answer(
        await get_change_menu_text(message), 
        parse_mode='Markdown',
        reply_markup=await get_kb_with_change_history(message)
    )

async def change_help(message: types.Message):

    args = message.get_args()
    if args.replace(' ', '') == '' or args == None:
        with open(TEXT_CHANGE_HELP_PATH, 'r', encoding = 'utf-8') as f:
            text = f.read()
            await message.answer(text)
    else:
        msg =await message.answer('📞 Бот-консультант готовит ответ...')
        await msg.edit_text(await AsyncGPT('202').tell_verify('У моего клиента следующий вопрос: {ask}. Ответь на него основываясь на прошлых ответах. Не придумывай ничего нового!!!! Напиши только ответ. Если вопрос не относится к боту, то пиши, что вопрос не по теме и не отвечай на него. Ты отвечаешь не мне, а клиенту. '.format(ask = args)))

# For Mailing
async def mailing_base(message: types.Message):

    with open(config.USERS_DATA_PATH + 'admin.json', 'r', encoding='utf-8') as file:
        admins = json.load(file)

    if message.from_user.id not in admins:
        await message.answer('Успешно!')
        return
    
    with open(config.MAILING_PATH + 'mailing.json', 'r', encoding='utf-8') as file:
        jf = json.load(file)

    image_path = jf['image_path']
    text = jf['text']
    goal_auditory = jf['goal_auditory']

    await bot.send_message(message.chat.id, 'Запускаем рассылку!')

    if image_path is None:
        res = await go_mailing(text, None, bot = bot, parse_mode='Markdown', in_users = 'ls' in goal_auditory, in_chats = 'chat' in goal_auditory)
    else:
        res = await go_mailing(text, image_path, bot = bot, parse_mode='Markdown', in_users = 'ls' in goal_auditory, in_chats = 'chat' in goal_auditory)
    
    errors = 'Без ошибок' if res[-1] == None else res[-1]
    missed_chats = 'Нет' if len(res[1]) == 0 else res[1]
    
    await bot.send_message(
        message.chat.id, 
        'Рассылка успешно выполнена!\n*Ошибки:* {ers}\n*Пропущенные чаты:* {mchts}'.format(ers = errors, mchts = missed_chats),
        parse_mode = 'Markdown'
    )

    # if image_path is not None:
    #     os.remove(image_path)

# Reactions
async def join_in_group_reaction(message: types.Message):
    for member in message.new_chat_members:
        if member.id == bot.id:
            with open(TEXT_JOIN_IN_GROUP_PATH, 'r', encoding='utf-8') as f:
                text = f.read()
                await message.answer(text)
                return

# Others
async def remove_buttons(message: types.Message):
    await message.answer('Кнопки убраны', reply_markup=ReplyKeyboardRemove())

async def next(message: types.Message):
    gpt = AsyncGPT(message.from_user.id)
    ans = await gpt.tell_next('standart')
    await message.answer(ans)
    #await global_tell(message, "", message.from_user.id)

def register_handlers(dp: Dispatcher):
    
    # reactions finctions
    dp.register_message_handler(join_in_group_reaction, content_types=[types.ContentType.NEW_CHAT_MEMBERS])

    # base functions
    dp.register_message_handler(start, commands = ['start'])
    dp.register_message_handler(help, commands = ['help'])
    dp.register_message_handler(reset, commands = ['reset'])
    dp.register_message_handler(reset_public, commands = ['reset_public'])
    #dp.register_message_handler(edit_key, commands = ['login'])

    # other tell finctions
    dp.register_message_handler(tell_public, commands = ['tell'])
    dp.register_message_handler(tell_private, commands = ['ls'])
    dp.register_message_handler(next, commands=['next'])

    # function for mailing
    dp.register_message_handler(mailing_base, commands = ['start_mailing', 'stm'])

    # handlering voice content
    dp.register_message_handler(tell_voice, content_types=[types.ContentType.VOICE])
    dp.register_message_handler(tell_voice, content_types=[types.ContentType.AUDIO])
    dp.register_message_handler(tell_video_note, content_types=[types.ContentType.VIDEO_NOTE])

    # change functions
    dp.register_message_handler(change,commands=['change'])
    dp.register_message_handler(change_help, commands='change_help')
    dp.register_callback_query_handler(buttons_handler, lambda c: True)
    dp.register_message_handler(edit_keywords, state = EditParameters.keywords)

    # IMAGE GENERATED functions
    dp.register_message_handler(get_image, commands = ['image'])
    dp.register_message_handler(get_image_stable, commands = ['image_stable'])

    # handlering text content
    dp.register_message_handler(tell, chat_type = types.ChatType.PRIVATE)
