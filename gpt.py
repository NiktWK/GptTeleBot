import os, json, config
import openai
openai.api_key = os.environ['OPENAI_API_KEY']

messages=[]

"users.json"
class GPT:
  def __init__(self, id): # id - id юзера
    with open('user.json', 'r') as f:
        self.jf = json.load(f)
    
    self.id = id
    if not id in self.jf:
      self.jf[id] = {'messages': []}
      with open('user.json', 'w') as f:
        json.dump(self.jf, f)
      
      with open('user.json', 'r') as f:
        self.jf = json.load(f)

    self.messages = self.jf[id]['messages']
    self.lastresponse = 'None'

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
      json.dump(self.jf, f)

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

  def edit_key(newkey: str):
    if newkey[0:2] == "sk":
      open("key.bin", "w").write(newkey)
      os.environ["OPENAI_API_KEY"] = newkey
      openai.api_key = newkey