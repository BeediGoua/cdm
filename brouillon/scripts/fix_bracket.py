import json

filepath = r"c:\Users\gouab\Desktop\Projet_perso\cdm\src\data\normalized\bracketRules.json"
with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data.get("roundOf32", []):
    if item.get("awaySlotOptions"):
        new_opts = []
        for opt in item["awaySlotOptions"]:
            if len(opt) == 1:
                new_opts.append("3" + opt)
            else:
                new_opts.append(opt)
        item["awaySlotOptions"] = new_opts

with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("bracketRules.json mis à jour avec succès.")
