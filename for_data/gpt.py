import requests, sys, os, uuid, json
sys.path.insert(1 , os.path.join(sys.path[0], '..'))
from config import MESSAGES_PATH, MESSAGE_CONFIGURE
from for_data.connect import connect

import aiohttp, config
from for_data.ad import *
from datetime import datetime
import openai, requests, asyncio, re

Q_MESSAGES_AD = 10
DELETE_TOKENS = 2000
MaxAttemptDiffusion = 2

USER_STRUCT = {
  'processing': False, 
  'count': 0, 
  'answer-type': 'text',
  'save-history': True,
  'messages': []
}
GROUP_STRUCT = {
  'processing': False, 
  'count': 0, 
  'answer-type': 'text',
  'save-history': True,
  'answer-voice-chat': 'recognition', # 'summary' 'None'
  'keywords': ['бот', 'bot', 'gpt'],
  'messages': []
}

HEADERS = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + os.environ['OPENAI_API_KEY']
}
URL_DALLE = "https://api.openai.com/v1/images/generations"
URL_GPT = "https://api.openai.com/v1/chat/completions"
URL_STABLEDIFFUSION = "https://stablediffusionapi.com/api/v3/text2img"
URL_STABLEDIFFUSION_IMG2IMG = "https://stablediffusionapi.com/api/v3/img2img"

async def download_http(url):
    filedata = requests.get(url)
    return filedata.content

def download_http_Stat(url):
    filedata = requests.get(url)
    return filedata.content

# Exceptions
class AlreadyProcessingError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

# Supported classes
class Messages:
  def __init__(self, id_, types = 'standart', save_history = True):
    with open(f'{config.MESSAGES_PATH}messages.json', 'r') as f:
        self.all_messages = json.load(f)

    self.id_ = str(id_)
    if not self.id_ in self.all_messages:
      self.all_messages[self.id_] = MESSAGE_CONFIGURE
      with open(f'{config.MESSAGES_PATH}messages.json', 'w', encoding='utf-8') as f:
        json.dump(self.all_messages, f, indent=4)

    self.messages = self.all_messages[self.id_]
    
    self.types = types
    self.user = self.messages[types]
    self.no_delete = self.get_no_delete(types)
    self.save_history = save_history

  def get(self):
    self.save()
    return self.no_delete + self.user
  
  def new_type(self, types):
    self.save()
    self.types = types

    if types not in self.messages:
      self.user = []
      self.save()

    self.user = self.messages[types]
    self.no_delete = self.get_no_delete(types)

  def get_no_delete(self, types):
    with open(f'{config.USERS_DATA_PATH}no_delete.json', 'r') as f:
        no_delete = json.load(f)
        return no_delete[types]

  def save(self):    
    self.messages[self.types] = self.user
    self.all_messages[self.id_] = self.messages

    if self.save_history:
      with open(f'{config.MESSAGES_PATH}messages.json', 'w', encoding='utf-8') as f:
          json.dump(self.all_messages, f, indent=4)

    # save_history

  def clear(self):
    self.user = []
    self.save()

  def deleteLast(self, index = 1):
    if index < len(self.user): 
        self.user = self.user[index:]
        self.save()
    elif index == len(self.user):
      self.user = []


  def add(self, el):

    if self.save_history:
        self.user.append(el)
    else:
      if len(self.user) < 1:
        self.user.append(el)
      else:
        self.user[-1] = el

class User:
  group_name = 'user'
  def __init__(self, id_):
    conn = connect()
    with conn.cursor() as cursor:
      cursor.execute('SELECT * FROM "{}" WHERE id = %s'.format(self.group_name), [id_,])
      user_data = cursor.fetchone()

    self.id_ = id_
    if user_data == None:
      user_data = self.create()
    
    self.lastresponse = None
    self.mcount = user_data[1]
    self.processing = user_data[2]
    self.answer_type = user_data[3]
    self.save_history = user_data[4]
    self.vip = user_data[5]
    self.is_chat = False

  def save(self):
    conn = connect()
    with conn.cursor() as cursor:
      cursor.execute('UPDATE "{}" SET count = %s, processing = %s, answer_type = %s, save_history = %s, vip = %s WHERE id = %s'.format(
          self.group_name
        ), [
        self.mcount,

        self.processing,
        self.answer_type,
        self.save_history,
        self.vip,
        self.id_
      ])
      conn.commit()
      cursor.close()

  def edit_property(self, property_: str, value: bool):
    conn = connect()
    with conn.cursor() as cursor:
      cursor.execute('UPDATE "{}" SET {} = %s WHERE id = %s'.format(self.group_name, property_), [
        value,
        self.id_
      ])
      conn.commit()
      cursor.close()
  
  def edit_processing(self, value):
    self.edit_property('processing', value)
    self.processing = value
  
  def create(self):
    conn = connect()
    with conn.cursor() as cursor:
      cursor.execute('INSERT INTO "{}" (id) VALUES (%s)'.format(self.group_name), [self.id_, ])
      conn.commit()

      cursor.execute('SELECT * FROM "{}" WHERE id = %s'.format(self.group_name), [self.id_,])
      res = cursor.fetchone()
      cursor.close()
    return res
  
  @property
  def count(self):
    return self.mcount
  
  @count.setter
  def count(self, value):
    self.edit_property('count', value)
    self.mcount = value

class Chat(User):
  group_name = 'chat'
  def __init__(self, id_):
    super().__init__(id_)
    conn = connect()
    with conn.cursor() as cursor:
      cursor.execute('SELECT * FROM "{}" WHERE id = %s'.format(self.group_name), [id_,])
      chat_data = cursor.fetchone()
    self.keywords_s = chat_data[-2]
    self.answer_voice_chat = chat_data[-1]
    self.is_chat = True

  @property
  def keywords(self):
    return self.keywords_s.split(',')
  
  @keywords.setter
  def keywords(self, value: list):
    self.keywords_s = ','.join([i.lower() for i in value])
    self.save()

  def save(self):
    super().save()
    conn = connect()
    with conn.cursor() as cursor:
      cursor.execute("UPDATE \"{}\" SET keywords = '{}', answer_voice_chat = '{}' WHERE id = %s".format(
        self.group_name, self.keywords_s, self.answer_voice_chat
        ), [self.id_,]
      )
    conn.commit()
    cursor.close()

class ChatUser(Chat):
  group_name = 'user'
  def __init__(self, id_, chat_id):
    User().__init__(id_)
    self.chat_id = chat_id
    conn = connect()
    with conn.cursor() as cursor:
      cursor.execute('SELECT * FROM "settings" WHERE user_id = %s and chat_id = %s', [id_, chat_id])
      chat_data = cursor.fetchone()
    self.keywords_s = chat_data[-2]
    self.answer_voice_chat = chat_data[-1]
    self.is_chat = True

  def save(self):
    User().save()
    conn = connect()
    with conn.cursor() as cursor:
      cursor.execute("UPDATE \"settings\" SET keywords = '{}', answer_voice_chat = '{}' WHERE user_id = %s and chat_id = %s".format(
        self.keywords_s, self.answer_voice_chat
        ), [self.id_, self.chat_id]
      )
    conn.commit()
    cursor.close()
    
# GPT classes -> usually and async versions
class GPT():
  def __init__(self, id, is_chat = False, is_chat_user = False): # id - id юзера
    id = str(id)
    self.id = id

    if is_chat_user:
      self.user = ChatUser(self.id)
    elif is_chat:
      self.user = Chat(self.id)
    else:
      self.user = User(self.id)

    self.messages = Messages(self.id, save_history=self.user.save_history)
    
  def reset(self, types = 'standart'):
    self.messages.new_type(types)
    self.messages.clear()
    self.edit_processing(False)

  def save(self):
    self.messages.save()
    self.user.save()

  def edit_processing(self, value: bool):
    self.user.edit_processing(value)
  
  @property
  def count(self):
    return self.user.count
  
  @count.setter
  def count(self, value):
    self.user.count = value

  @property
  def processing(self):
    return self.user.processing
  
  @property
  def save_history(self):
    return self.user.save_history
  
  def ad(self):
    if self.count % Q_MESSAGES_AD == 0:
      ad = get()
      self.count = 0
      self.save()
      return ad
    return False
  
  def try_DALLE(prompt : str):
    data = {
      "model": "image-alpha-001",
      "prompt": prompt,
      "num_images": 1,
      "size": "256x256",
      "response_format": "url"
    }

    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
    }

    response = requests.post(URL_DALLE, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        result = response.json()
        image_url = result["data"][0]["url"]
        with open('data/images_data.json', 'w') as jf:
          json.dump(result, jf, indent=4)
        return image_url
    
    return "Error:" + str(response.status_code)

  def stt(file):
    audio_file = file
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript['text']
  
  def edit_save_history(self, save_history_is = True):
    self.user.save_history = save_history_is
    self.user.edit_property('save_history', save_history_is)

  def edit_keywords(self, new_keywords: list):
    if self.user.is_chat:
      self.user.keywords = new_keywords

  def edit_answer_voice_chat(self, answer_voice_chat: str):
    if answer_voice_chat not in ['auto', 'recognition', 'summary', 'none'] or not self.user.is_chat:
      return False
    self.user.answer_voice_chat = answer_voice_chat
    self.user.save()

  def edit_answer_type(self, answer_type: str):
    if answer_type not in ['text', 'voice', 'text-and-voice']:
      return False
    self.user.answer_type = answer_type
    self.user.save()

  def set_prime(self, value = True):
    self.user.vip = value
    self.save()

class AsyncGPT(GPT):
  # for sending request and getting response
  @staticmethod
  async def requests_result(session, url = URL_GPT, headers = HEADERS, **kwargs):
    async with session.post(url, headers = headers, **kwargs) as result:
      res = result
      res1 = await res.json()

      return res1

  # for getting a request response with self.messages as messages
  @staticmethod
  async def get_response(**kwargs):
    async with aiohttp.ClientSession() as session:
      result = await AsyncGPT.requests_result(session, **kwargs)
      return result

  def __init__(self, id, is_chat=False):
    super().__init__(id, is_chat)
    self.gpt35_model = 'gpt-3.5-turbo'

  async def tell_process(self, types):
    self.messages.new_type(types)
    process = True
    time_start = datetime.now()

    completion = None
    while process:
      try:
        completion = await self.get_response(json = {'model': self.gpt35_model, 'messages': self.messages.get()})
        chat_response = completion['choices'][0]['message']['content']
        process = False

      except Exception as er:
        if len(self.messages.user) < 2:
          self.edit_processing(False)
          raise IndexError()
        
        else:
          self.messages.deleteLast(2)
          self.messages.save()
          await asyncio.sleep(15)

    delta = datetime.now() - time_start
    if delta.seconds > 40 and process:
        self.edit_processing(False)
        raise TimeoutError()
    return chat_response
  
  async def tell_verify(self, question, types : str = 'standart', save = True):
    if self.user.processing:
      raise AlreadyProcessingError()
    
    self.messages.save_history = save
    self.user.edit_processing(True)
    self.messages.new_type(types)
    self.messages.add({"role": "user", "content": question})
    
    chat_response = await self.tell_process(types)
    self.count += 1

    self.messages.add({"role": "assistant", "content": chat_response})
    
    self.edit_processing(False)
    self.save()
  
    self.user.lastresponse = chat_response
    return chat_response
  
  async def tell_next(self, types):    
    self.messages.deleteLast()
    self.messages.new_type(types)
    res = await self.tell_process(types)
    self.messages.add({'role': 'assistant', 'content': res})
    self.messages.save()
    return res

  async def try_DALLE(self, prompt : str):
    data = {
      "prompt": prompt,
      "num_images": 1,
      "size": "512x512",
      "response_format": "url"
    }

    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
    }

    result = await AsyncGPT.get_response(url = URL_DALLE, headers=headers, json = data)

    self.count += 1
    self.save()
    
    if 'data' in result:
        image_url = result["data"][0]["url"]
        return image_url
    
    return ["error", result['error']]
  
  async def try_Diffusion(self, prompt : str, count = 0):
    srcs = re.findall(r'(https?://\S+)', prompt)

    if len(srcs) == 0:
      data = {
        "key": os.environ['STABLEDIFFUSION_API_KEY'],
        "prompt": prompt,
        "negative_prompt": "((out of frame))",
        "width": "512",
        "height": "512",
        "samples": "1",
        "num_inference_steps": "20",
        "seed": None,
        "guidance_scale": 7.5,
        "safety_checker":"yes",
        "webhook": None,
        "track_id": None
      }
      url = URL_STABLEDIFFUSION
    else:
      for src in srcs:
        prompt = prompt.replace(src, '')

      data = {
        "key": os.environ['STABLEDIFFUSION_API_KEY'],
        "prompt": prompt,
        "init_image": srcs[0],
        "negative_prompt": "((out of frame))",
        "width": "512",
        "height": "512",
        "samples": "3",
        "num_inference_steps": "20",
        "seed": None,
        "guidance_scale": 7.5,
        "safety_checker":"yes",
        "webhook": None,
        "track_id": None
      }
      url = URL_STABLEDIFFUSION_IMG2IMG
    headers = {
      "Content-Type": "application/json"
    }

    result = await AsyncGPT.get_response(url = url, headers=headers, json = data)
    self.count += 1
    self.save()

    try:
      if 'output' in result:
          image_url = result["output"]
          return image_url
      
      return ["error", {"message":'Ваш пробный период закончен.'}]
    except:
      return ["error", {"message":'Извините, ошибка. Попробуйте еще раз.'}]
  
  @staticmethod
  async def transcribe(file):
    data = aiohttp.FormData()
    data.add_field('file', file)
    data.add_field('model', 'whisper-1')
    headers = {
        'Authorization': 'Bearer ' + os.environ["OPENAI_API_KEY"]
    }

    url = "https://api.openai.com/v1/audio/transcriptions"
    
    async with aiohttp.ClientSession() as session:
      response = await AsyncGPT.requests_result(session, url=url, headers=headers, data=data)


    return response['text']

if __name__ == "__main__":
  print(Messages.get_no_delete(None, "rewrite"))