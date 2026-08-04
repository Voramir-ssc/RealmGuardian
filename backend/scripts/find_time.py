import json

with open("debug_char_Dorchada.json", encoding="utf-8") as f:
    data = json.load(f)

def find_all(categories):
    res = []
    for c in categories:
        res.extend(find_all(c.get("sub_categories", [])))
        for s in c.get("statistics", []):
            res.append((s.get("name"), s.get("quantity")))
    return res

names = [r[0] for r in find_all(data.get("stats", {}).get("categories", []))]
print(len(names))
with open("all_stats.txt", "w", encoding="utf-8") as out:
    for n in names:
        if n: out.write(n + "\n")
