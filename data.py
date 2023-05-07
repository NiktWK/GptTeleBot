import json
with open('data.json', 'r') as file:
    j = json.load(file)

with open('data.json', 'w', encoding='utf-8') as file:
    json.dump(j, file, ensure_ascii=False, indent=4)