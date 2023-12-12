from random import randrange
import sys, os
sys.path.insert(1 , os.path.join(sys.path[0], '..'))
import json, config
from config import USERS_DATA_PATH, AD_PATH
from for_data.connect import connect
AD_STRUCTURE = {
    "header": "None",
    "shows": -1,
    "text": "None",
    "image-path": "None",
    "max-shows": -1
}

def image(path: str):
    return open(path, 'rb')

class Ad():
    def __init__(self, id, empty = False):
        
        with open(f'{AD_PATH}ads.json', encoding = 'utf-8') as file:
                ads = json.load(file)

        if not empty: 
            self.id = str(id)  
            ad = ads[self.id]  
        else:
            ad = AD_STRUCTURE
            self.id = str(int(list(ads.keys())[-1]) + 1)
        
        self.ad = ad
        self.text = ad['text']
        self.countt = ad['shows']
        self.max_shows = ad['max-shows']
        self.image_path = ad['image-path']

        if self.image_path is not None:
            self.image = image(self.image_path)
        else:
            self.image = None
        
    def saveObj(self):
        self.ad["image-path"] = self.image_path
        self.ad["text"] = self.text
        self.ad["max-shows"] = self.max_shows
        self.ad["shows"] = self.count

    def save(self, ad = None):
        with open(f'{AD_PATH}ads.json', encoding = 'utf-8') as file:
            ads = json.load(file)
            if ad is None:
                self.saveObj()
                ads[str(self.id)] = self.ad
            else:
                ads[str(self.id)] = ad

        with open(f'{config.AD_PATH}ads.json', 'w', encoding = 'utf-8') as file:
            json.dump(ads, file, ensure_ascii=False, indent = 4)

    @property
    def count(self):
        return self.countt # кол-во показов
    
    @count.setter
    def count(self, value):
        self.countt = value
        self.save()

def get() -> Ad:
    with open(f'{config.AD_PATH}ads.json', 'r') as file:
        jfile = json.load(file)
        maxc = int(list(jfile.keys())[-1])
        c = 0

        while True:
            ad = Ad(randrange(0, maxc+1))

            if ad.count <= ad.max_shows:
                ad.count += 1
                return ad
            
            if c > maxc*4:
                return False
            
            c+=1
  
def load_ad(id, path = f'{config.AD_PATH}newads.json'):
    with open(path, "r", encoding="utf-8") as file:
        jf = json.load(file)
        if id == -2:
            return jf
        elif id == -1:
            return jf[str(list(jf.keys())[-1])]
        else:
            return jf[str(id)]

def dump_ad(id, ad : Ad, new = False, path = f'{config.AD_PATH}newads.json'):
    ad.saveObj()
    jf = load_ad(-2, path)
    with open(path, "w", encoding="utf-8") as file:
        keys = list(jf.keys())
        if new:
            if len(keys) == 0:
                id = 0
            else:
                id = int(keys[-1]) + 1
        elif id == -1:
            if len(keys) == 0:
                id = 0
            else:
                id = int(keys[-1])
        jf[str(id)] = ad.obj 

        json.dump(jf, file, ensure_ascii=False, indent = 4)
        file.close()
    
def replace_ad(id, ad: Ad, path_from = f'{config.AD_PATH}newads.json', path_in = f'{config.AD_PATH}ads.json'):
    ad.saveObj()
    with open(path_from, "r", encoding="utf-8") as file_from:
        jf_from = json.load(file_from)
        file_from.close()

    if id == -1:
        id = int(list(jf_from.keys())[-1])

    dump_ad(-1, ad, new = True, path = path_in)

    with open(path_from, "w", encoding="utf-8") as file_from:
        jf_from.pop(str(id))
        json.dump(jf_from, file_from, ensure_ascii=False, indent=4)
        file_from.close()

def get_chats(in_chats = False, in_users = False):
    con = connect()
    users = []
    chats = []

    with con.cursor() as cursor:
        
        if in_users:
            cursor.execute('SELECT * FROM "user"')
            users = cursor.fetchall()
        if in_chats:
            cursor.execute('SELECT * FROM "chat"')
            chats = cursor.fetchall()
        all_ids = [chat[0] for chat in chats+users]

        return all_ids
