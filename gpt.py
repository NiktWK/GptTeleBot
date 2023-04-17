import os, json, config
import openai
openai.api_key = os.environ['OPENAI_API_KEY']

messages=[]

class GPT:
  def __init__(self, id): # id - id юзера
    self.jf = json.load(open('users.json', 'r'))
    self.id = id
    if not id in self.jf:
      self.jf[id] = {'messages': []}
      json.dump(self.jf, open('users.json', 'w'))
      self.jf = json.load(open('users.json', 'r'))

    self.messages = self.jf[id]['messages']
    self.lastresponse = 'None'

  def reset(self):
    self.jf[self.id]['messages'] = []
    json.dump(self.jf, open('users.json', 'w'))
    
  def save(self):
    self.jf[self.id]['messages'] = self.messages
    json.dump(self.jf, open('users.json', 'w'))

  def tell(self, question):
    self.messages.append({"role": "user", "content": question})
    completion = openai.ChatCompletion.create(model = 'gpt-3.5-turbo', messages = self.messages)
    chat_response = completion.choices[0].message.content
    self.messages.append({"role": "assistant", "content": chat_response})
    self.save()
    self.lastresponse = chat_response
    return chat_response

  def offline_talks(self):
    q = input('User: ')
    while q != 'end':
      print('ChatGPT:', self.tell(q))
      q = input('User: ')