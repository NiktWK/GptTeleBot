import os

os.environ["OPENAI_API_KEY"] = open("key_ai.bin", "r").read()
os.environ["TELEGRAM_BOT_TOKEN"] = "6153578045:AAHCVQnlzrw8Oarmc8ZWViyYHooykDJqtwY"
os.environ["STABLEDIFFUSION_API_KEY"] = open("key_stable.bin", "r").read()