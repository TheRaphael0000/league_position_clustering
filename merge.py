import json
import glob

matches = []

files = glob.glob("data/*.json")
for file_ in files:
    matches += json.load(open(file_))
    print(len(matches))
json.dump(matches, open("data/matches.json", "w"))