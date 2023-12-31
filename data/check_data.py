import json

move_set_0 = set()
with open("./moves.json", "r") as f:
    moves = json.loads(f.read())

for move in moves:
    move_set_0.add(move["name"])

with open("./dex.json", "r") as f:
    dex = json.loads(f.read())

print("pause")
move_set = set()
for species in dex.keys():
    if dex[species]["index"] > 150:
        continue
    for move in dex[species]["moves"]:
        move_set.add(move["name"])

move_set.intersection(move_set)