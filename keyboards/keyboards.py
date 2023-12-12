from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

answer_voice_chat_edit = InlineKeyboardButton('Ответ на глс. Сообщения', callback_data='answer_voice_chat_edit')
answer_type_edit = InlineKeyboardButton('Тип Ответа', callback_data='answer_type_edit')
keywords_edit = InlineKeyboardButton('Ключевые Слова для Вызова', callback_data='keywords_edit')
save_history_delete = InlineKeyboardButton('Не сохранять историю', callback_data='save_history_delete')
save_history_go = InlineKeyboardButton('Сохранять историю', callback_data='save_history_go')

answer_voice_chat_auto = InlineKeyboardButton('Авто', callback_data='answer_voice_chat_auto')
answer_voice_chat_summary = InlineKeyboardButton('Краткое Содержание', callback_data='answer_voice_chat_summary')
answer_voice_chat_recognition = InlineKeyboardButton('Распознанная Речь', callback_data='answer_voice_chat_recognition')
answer_voice_chat_none = InlineKeyboardButton('Ничего', callback_data='answer_voice_chat_none')

answer_type_voice = InlineKeyboardButton('Голосовое Сообщение', callback_data='answer_type_voice')
answer_type_text = InlineKeyboardButton('Текст', callback_data='answer_type_text')
answer_type_text_and_voice = InlineKeyboardButton('Текст и Голосовое Сообщение', callback_data='answer_type_text_and_voice')

back = InlineKeyboardButton('Назад', callback_data='back')
back_r = KeyboardButton('Назад ↩️', callback_data='back')
answer_voice_chat_kb = InlineKeyboardMarkup(1, resize_keyboard = True).add(answer_voice_chat_summary, answer_voice_chat_recognition, answer_voice_chat_none, back)
answer_type_kb = InlineKeyboardMarkup(1, resize_keyboard = True).add(answer_type_text, answer_type_voice, back)
edit_list_group_kb = InlineKeyboardMarkup(1, resize_keyboard = True).add(answer_type_edit, answer_voice_chat_edit, keywords_edit)
edit_list_private_kb = InlineKeyboardMarkup(1, resize_keyboard = True).add(answer_type_edit)


# FOR Adminyanya
chats = InlineKeyboardButton('Чаты', callback_data='chats')
ls = InlineKeyboardButton('ЛС с ботом', callback_data='ls')
ls_and_chats = InlineKeyboardButton('ЛС и Чаты', callback_data='ls_and_chats')
goal_audit_kb = InlineKeyboardMarkup(1, resize_keyboard = True).add(chats, ls, ls_and_chats)

yes =  InlineKeyboardButton('Да', callback_data='yes')
no =  InlineKeyboardButton('Нет', callback_data='no')
yes_no_kb = InlineKeyboardMarkup(1, resize_keyboard = True).add(yes, no)

empty_kb = InlineKeyboardMarkup()


# ReplyKeyboards
generate_image = KeyboardButton('🖼 Создать картинку')
help_b = KeyboardButton('🧯 Помощь')
settings = KeyboardButton('🛠 Настройки')
help_settings = KeyboardButton('Помощь по настройке')
reset_b = KeyboardButton('🔄 Сбросить')
servises = KeyboardButton('✍️ Сервисы')

base_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(servises, generate_image, reset_b).add(help_b, settings)
settings_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(help_settings, back)
back_reset_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(reset_b).add(back_r)

# Serivses
rewrite = KeyboardButton('Рерайтинг')
forstudy = KeyboardButton('Для учебы')
post = KeyboardButton('Пост/Статья')
programming = KeyboardButton('Программирование')


servises_kb = ReplyKeyboardMarkup().add(rewrite, forstudy).add(post, programming).add(back_r)