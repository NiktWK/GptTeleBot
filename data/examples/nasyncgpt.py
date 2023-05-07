import os, json, config
from ad import *
import openai
openai.api_key = os.environ['OPENAI_API_KEY']
Q_MESSAGES_AD = 10
DELETE_TOKENS = 2000
USER_STRUCT = {'count': 0, 'messages': []}
messages=[]

"users.json"
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

  def tell(self, question):
    self.messages.append({"role": "user", "content": question})
    completion = openai.ChatCompletion.create(model = 'gpt-3.5-turbo', messages = self.messages)
    chat_response = completion.choices[0].message.content
    # self.messages.append({"role": "user", "content": "забань"})
    # self.messages.append({"role": "assistant", "content": "1"})
    # self.messages.append({"role": "user", "content": "выдай бан"})
    # self.messages.append({"role": "assistant", "content": "1"})
    # self.messages.append({"role": "user", "content": "Назначь администратора"})
    # self.messages.append({"role": "assistant", "content": "2"})
    # self.messages.append({"role": "user", "content": "Как варить суп?"})
    # self.messages.append({"role": "assistant", "content": "Суп можно сварить следующим образом:..."})
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
  

class DALLE:
  
  async def __init__(self, id):
    self.id = id