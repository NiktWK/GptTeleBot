from random import randrange
import json

AD_STRUCTURE = {
    "header": "None",
    "count": -1,
    "text": "None",
    "image": "None",
    "max-shows": -1
}

def image(path: str):
    return open(path, 'rb')

class Ad():
    def __init__(self, id, ad_type = 'exist', empty = False):

        if not empty:
            if ad_type == 'exist':
                file_path = 'data/ads.json'
            elif ad_type == 'new':
                file_path = 'data/newads.json'

            with open(file_path, 'r', encoding = 'utf-8') as file:
                jfile = json.load(file)
                if id == -1:
                    self.id = int(list(jfile.keys())[-1])
                    self.obj = jfile[str(self.id)]
                else:    
                    self.obj = jfile[str(id)]
                    self.id = id

            self.countt = self.obj["count"]
            self.image_path = self.obj["image"] 

            if self.image_path != "None":
                self.image = image(self.image_path)
            else:
                self.image = "None"

            self.text = self.obj["text"] 
            self.max_shows = self.obj["max-shows"]
            self.header = self.obj["header"]
        else:
            self.obj = AD_STRUCTURE
            self.countt = AD_STRUCTURE["count"]
            self.image_path = AD_STRUCTURE["image"] 
            self.image = None
            self.text = AD_STRUCTURE["text"] 
            self.max_shows = AD_STRUCTURE["max-shows"]
            self.header = AD_STRUCTURE["header"]
         # кол-во показов
        

    def saveObj(self):
        self.obj["image"] = self.image_path
        self.obj["text"] = self.text
        self.obj["max-shows"] = self.max_shows
        self.obj["count"] = self.count
        self.obj["header"] = self.header

    def save(self):
        with open('data/ads.json', encoding = 'utf-8') as file:
            jfile = json.load(file)
            self.saveObj()
            jfile[str(self.id)] = self.obj

        with open('data/ads.json', 'w', encoding = 'utf-8') as file:
            json.dump(jfile, file, ensure_ascii=False, indent = 4)

    @property
    def count(self):
        return self.countt # кол-во показов
    
    @count.setter
    def count(self, value):
        self.countt = value
        self.save()

def get() -> Ad:
    with open('data/ads.json', 'r') as file:
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

    
def load_ad(id, path = "data/newads.json"):
    with open(path, "r", encoding="utf-8") as file:
        jf = json.load(file)
        if id == -2:
            return jf
        elif id == -1:
            return jf[str(list(jf.keys())[-1])]
        else:
            return jf[str(id)]

def dump_ad(id, ad : Ad, new = False, path = "data/newads.json"):
    
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
    
def replace_ad(id, ad: Ad, path_from = "data/newads.json", path_in = "data/ads.json"):
    ad.saveObj()
    load_ad(id, path_from)
    with open(path_from, "r", encoding="utf-8") as file_from:
        jf_from = json.load(file_from)
        file_from.close()

    if id == -1:
        id = int(list(jf_from.keys())[-1])
    
    obj = jf_from[str(id)]   

    dump_ad(-1, ad, new = True, path = path_in)

    with open(path_from, "w", encoding="utf-8") as file_from:
        jf_from.pop(str(id))
        json.dump(jf_from, file_from, ensure_ascii=False, indent=4)
        file_from.close()

