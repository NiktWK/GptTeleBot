import os

os.environ["OPENAI_API_KEY"] = open("key_ai.bin", "r").read()
os.environ["TELEGRAM_BOT_TOKEN"] = "6132201222:AAElYETIcG15lsuE_zX5sfWyHGE6dtjkceM"
os.environ["STABLEDIFFUSION_API_KEY"] = open("key_stable.bin", "r").read()