import os

KEYS_PATH = "data/keys/"
AD_PATH = "data/ads/"
MAILING_PATH = "data/mailing/"
IMAGE_PATH = "data/image/"
USERS_DATA_PATH = "data/users/"
MESSAGES_PATH = "data/users/"
TEXT_PATH = "data/texts/"
TEXT_CHANGE_HELP_PATH = TEXT_PATH + 'change_help.txt'
TEXT_JOIN_IN_GROUP_PATH = TEXT_PATH + 'join_in_group.txt'

os.environ["OPENAI_API_KEY"] = open(f"{KEYS_PATH}key_ai.bin", "r").read()
os.environ["TELEGRAM_BOT_TOKEN"] = open(f"{KEYS_PATH}token_bot.bin", "r").read() #"6153578045:AAHCVQnlzrw8Oarmc8ZWViyYHooykDJqtwY"
os.environ["STABLEDIFFUSION_API_KEY"] = open(f"{KEYS_PATH}key_stable.bin", "r").read()
TEMP_PATH = "data/temp/"

QUERY_POST = "Напиши пост. В начале поста укажи заголовок. Все напиши, руководствуясь следующим текстом:[{}]"

MESSAGE_CONFIGURE = {
        'standart' : [],
        'post': [],
        'study': [],
        'rewrite': []
    }

AD_STYLE = "{text}"