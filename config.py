import os

os.environ["OPENAI_API_KEY"] = open("key_ai.bin", "r").read()
os.environ["TELEGRAM_BOT_TOKEN"] = "5878516157:AAGMOY4hExzI8a725L3ePEuBTAPgZdZ5Mh4"
os.environ["STABLEDIFFUSION_API_KEY"] = open("key_stable.bin", "r").read()