import asyncio
import os, json, config
import aiohttp
from ad import *
import openai, requests, numpy as np, base64, io, re
from PIL import Image
openai.api_key = os.environ['OPENAI_API_KEY']

Q_MESSAGES_AD = 10
DELETE_TOKENS = 2000
MaxAttemptDiffusion = 2
USER_STRUCT = {'count': 0, 'messages': []}
HEADERS = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + os.environ['OPENAI_API_KEY']
}
URL_DALLE = "https://api.openai.com/v1/images/generations"
URL_GPT = "https://api.openai.com/v1/chat/completions"
URL_STABLEDIFFUSION = "https://stablediffusionapi.com/api/v3/text2img"
URL_STABLEDIFFUSION_IMG2IMG = "https://stablediffusionapi.com/api/v3/img2img"

messages=[]

async def download_http(url):
    filedata = requests.get(url)
    return filedata.content

def download_http_Stat(url):
    filedata = requests.get(url)
    return filedata.content

class GPT:
  def __init__(self, id): # id - id юзера
    with open('user.json', 'r') as f:
        self.jf = json.load(f)
    
    self.id = id
    if not id in self.jf:
      self.jf[id] = USER_STRUCT
      with open('user.json', 'w') as f:
        json.dump(self.jf, f)
      
      with open('user.json', 'r') as f:
        self.jf = json.load(f)

    self.messages = self.jf[id]['messages']
    self.lastresponse = 'None'
    self.mcount = self.jf[id]['count']

  def reset(self):
    self.jf[self.id]['messages'] = []
    with open('user.json', 'w') as f:
        json.dump(self.jf, f)

  def deleteLast(self, index = 1):
    if len(self.jf[self.id]['messages']) > index:
      self.jf[self.id]['messages'] = self.jf[self.id]['messages'][index:]

  def save(self):
    self.jf[self.id]['messages'] = self.messages
    with open('user.json', 'w') as f:
      json.dump(self.jf, f, indent = 4)

  @property
  def count(self):
    return self.jf[self.id]['count']
  
  @count.setter
  def count(self, value):
    self.jf[self.id]['count'] = value

  async def tell(self, question):
    self.messages.append({"role": "user", "content": question})
    completion = openai.ChatCompletion.create(model = 'gpt-3.5-turbo', messages = self.messages)
    chat_response = completion.choices[0].message.content
    self.count += 1
    self.messages.append({"role": "assistant", "content": chat_response})
    self.save()
    self.lastresponse = chat_response
    return chat_response

  def offline_talks(self):
    q = input('User: ')
    while q != 'end':
      print('ChatGPT:', self.tell(q))
      q = input('User: ')

  def deleteTokens(self):
    self.save()

    summ = 0
    i = 0
    for el in self.jf[self.id]['messages']:
      summ += len(el['content'])
      i+=1

      if summ >= DELETE_TOKENS:
        break

    self.jf[self.id]['messages'] = self.jf[self.id]['messages'][i:]
    self.messages = self.jf[self.id]['messages']
    self.save()

  def edit_key(newkey: str):
    if newkey[0:2] == "sk":
      open("key.bin", "w").write(newkey)
      os.environ["OPENAI_API_KEY"] = newkey
      openai.api_key = newkey

  def ad(self):
    print(self.count)
    if self.count % Q_MESSAGES_AD == 0:
      ad = get()
      self.count = 0
      self.save()
      return ad
    
    #self.count += 1
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
        return image_url
    
    return "Error:" + str(response.status_code)

class AsyncGPT(GPT):

  async def requests_result(session, messages = [], url = URL_GPT, headers = HEADERS, data = None):

    if data == None:
      data = {
        'model': 'gpt-3.5-turbo',
        'messages': messages
      }

    async with session.post(url, headers = headers, json = data) as result:
      return await result.json()
    
  async def get_response(self):
    async with aiohttp.ClientSession() as session:
      result = AsyncGPT.requests_result(session, self.messages)
      return await result
    
  async def tell(self, question):
    self.messages.append({"role": "user", "content": question})

    completion = await self.get_response()

    if not 'choices' in completion:
      return
    else:
      chat_response = completion['choices'][0]['message']['content']
    
      self.count += 1
      self.messages.append({"role": "assistant", "content": chat_response})
      self.save()
      self.lastresponse = chat_response
      return chat_response
    
  async def try_DALLE(self, prompt : str):
    data = {
      "model": "image-alpha-001",
      "prompt": prompt,
      "num_images": 1,
      "size": "512x512",
      "response_format": "url"
    }

    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
    }

    async with aiohttp.ClientSession() as session:
      result = await AsyncGPT.requests_result(session, url = URL_DALLE, headers=headers, data = data)

    self.count += 1
    self.save()
    
    if 'data' in result:
        image_url = result["data"][0]["url"]
        return image_url
    
    return ["error", result['error']]
  
  async def try_Diffusion(self, prompt : str, count = 0):

    #img = download_http(img_src)
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
        "samples": "1",
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

    async with aiohttp.ClientSession() as session:
      result = await AsyncGPT.requests_result(session, url = url, headers=headers, data = data)
    print(result)
    self.count += 1
    self.save()
    print(result)
    try:
      if 'output' in result:
          image_url = result["output"][0]
          return image_url
      
      return ["error", {"message":'Ваш пробный период закончен.'}]
    except:
      return ["error", {"message":'Извините, ошибка. Попробуйте еще раз.'}]


class Img():
  def __init__(self, img_path = None, img_src = None, width = 300, height = 300):
    self.path = img_path
    self.src = img_src
    if self.src:
      self.img = download_http_Stat(self.src)
    else:
      self.img = open(img_path, 'rb')
    
    np_img = np.fromfile(self.img, dtype=np.uint8, count = width*height).reshape(height, width)

    self.PIL_img = Image.fromarray(np_img)

class Diffusion():
  def __init__(self, url):
    self.url = url

  def option_img2img(self):
    option_payload = {
    "sd_model_checkpoint": "sd-v1-5-inpainting.ckpt",
    "do_not_add_watermark": True
    }

    requests.post(url=f'{self.url}/sdapi/v1/options', json=option_payload)

  def img2img(self, p_env, n_p_mod, im:Image):
      self.option_img2img()
      #im = im.PIL_img
      img_bytes = io.BytesIO()
      im.save(img_bytes, format='PNG')
      img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')

      img2img_payload = {
          "init_images": [img_base64],
          "prompt": p_env,
          "negative_prompt": n_p_mod,
          "denoising_strength": 0.9,
          "width": 512,
          "height": 768,
          "cfg_scale": 7,
          "sampler_name": "Euler a",
          "restore_faces": False,
          "steps": 30,
          "script_args": ["outpainting mk2", ]
      }

      img2img_response = requests.post(url=f'{self.url}/sdapi/v1/img2img', json=img2img_payload)

      r = img2img_response.json()
    
      for i in r['images']:
          image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))

      return image
  

#diffusion = Diffusion(url = URL_STABLEDIFFUSION)
#img = diffusion.img2img('dog to cat', '', Image.open('cat2.jpg').convert('RGB'))

#img.save('dog.png')

#print(AsyncGPT('1299115555').try_Diffusion('convert to dog'))