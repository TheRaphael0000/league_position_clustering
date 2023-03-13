import json
import sys
import random
import uuid
import zipfile
import os
from requests import HTTPError

from riotwatcher import LolWatcher

iterations = 10000
matches_for_each_summoner = 5
queue_id = 420  # 5v5 solo queue
server = "EUW1"
match_per_file = 500
initial_summoner = "Neeko Tesla"

config = json.load(open("config.json", "rb"))
lol_watcher = LolWatcher(config["riot_api_key"])

summoner_0 = lol_watcher.summoner.by_name(server, initial_summoner)
puuid_visited = set()
matches_visited = set()
puuid_pool = set([summoner_0["puuid"]])
matches = []


def save_matches():
    json_filename = f"{str(uuid.uuid4())}.json"
    json_filepath = f"matches/{json_filename}"
    json.dump(matches, open(json_filepath, "w"))
    zip_file = f"matches/{str(uuid.uuid4())}.zip"
    with zipfile.ZipFile(zip_file, "w", compression=zipfile.ZIP_LZMA) as zip_:
        zip_.write(json_filepath, arcname=json_filename)
    os.remove(json_filepath)


try:
    for i in range(iterations):
        print(len(puuid_visited), len(matches), len(puuid_pool))

        puuid_pool -= puuid_visited
        list_puuid_pool = list(puuid_pool)
        random.shuffle(list_puuid_pool)
        list_puuid_pool = list_puuid_pool[0:100]
        puuid_pool = set(list_puuid_pool)

        if len(puuid_pool) <= 0:
            break

        puuid = puuid_pool.pop()
        try:
            matches_id = lol_watcher.match.matchlist_by_puuid(
                server, puuid, count=matches_for_each_summoner, queue=queue_id)
        except HTTPError as e:
            print(e, file=sys.stderr)
            continue

        matches_id = set(matches_id)
        matches_id -= matches_visited
        puuid_visited.add(puuid)

        for match_id in matches_id:
            matches_visited.add(match_id)

            try:
                match = lol_watcher.match.by_id(server, match_id)
            except HTTPError as e:
                print(e, file=sys.stderr)
                continue

            # add participants to puuid pool
            puuid_pool |= set(match["metadata"]["participants"])

            matches.append(match)

            if len(matches) >= match_per_file:
                save_matches()
                matches = []

except KeyboardInterrupt as e:
    print(e, file=sys.stderr)

save_matches()
