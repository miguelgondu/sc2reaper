"""Main module."""
import json
import jsonschema
import os

from pathlib import Path
from jsonschema import validate
from typing import List
from pymongo import MongoClient
from pysc2 import run_configs
from sc2reaper.sweeper import extract_all_info_once

# Reading the set up from config.json found in the current working directory(cwd_):
<<<<<<< HEAD
with open(str(__file__).replace('sc2reaper.py', 'config.json')) as fp:
    config = json.load(fp)
    MATCH_UPS = config["MATCH_UPS"]
    DB_NAME = config["DB_NAME"]
    address = config["PORT_ADDRESS"]
    port_num = config["PORT_NUMBER"]
=======
cwd_ = Path.cwd()
config_ = (cwd_ / 'config.json')

config_schema = {
    "type": "object",
    "properties":{
        "DB_NAME": {"type":"string"},
        "STEP_MULT": {"type":"number"},
        "MATCH_UPS":  {"type":"array"},
        "SC2_PATH":  {"type":"string"},
        "PORT_ADDRESS":  {"type":"string"},
        "PORT_NUMBER": {"type":"number"}
    }
}

def validateConfig(config_json):
    try:
        validate(config_schema, config_json)
    except jsonschema.exceptions.ValidationError as err:
        return False
    except jsonschema.exceptions.SchemaError as err:
        print(err)
        print("The Config_schema is invalid")
        raise err
    
    return True


if config_.exists() and validateConfig(json.load(config_.open())):
    print("Loading according to local config.json")
    with config_.open() as fp:
        config = json.load(fp)
        MATCH_UPS = config["MATCH_UPS"]
        DB_NAME = config["DB_NAME"]
        address = config["PORT_ADDRESS"]
        port_num = config["PORT_NUMBER"]

else:
    print("Loading according to default config.json")
    default_config_path =  Path(__file__).parent / 'config.json'
    with default_config_path.open() as fp:
        config = json.load(fp)
        MATCH_UPS = config["MATCH_UPS"]
        DB_NAME = config["DB_NAME"]
        address = config["PORT_ADDRESS"]
        port_num = config["PORT_NUMBER"]
>>>>>>> ed773e7794ab82443bd7314a5cb9f4839ddd28fc

# Entering the mongo instance

def process_replays(replay_files, run_config, last_replay_processed=None):
    client = MongoClient(address, port_num)
    db = client[DB_NAME]
    replays_collection = db["replays"]
    players_collection = db["players"]
    states_collection = db["states"]
    actions_collection = db["actions"]
    scores_collection = db["scores"]

    if last_replay_processed:
        index = replay_files.index(last_replay_processed)
    else:
        index = -1

    try:
        with run_config.start() as controller:
            for replay_file in replay_files[index + 1:]:
                last_replay_processed = replay_file
                print(f"Processing replay {replay_file.name}")
                # And they wrap this in a try except too. (No exceptions in this case)
                replay_data = run_config.replay_data(replay_file)
                info = controller.replay_info(replay_data)

                if info.game_duration_loops < 500:
                    print(f"Replay {replay_file} is too short.")
                    continue
                
                upper_bound = 22 * 60 * 60 * 1.5
                if info.game_duration_loops > upper_bound:
                    print(f"Replay {replay_file} is too long (> 1.5 hours)")
                    continue

                map_data = None
                if info.local_map_path:
                    map_data = run_config.map_data(info.local_map_path)

                # Extracting general information for the replay document

                ## Extracting the Match-up
                player_1_race = info.player_info[0].player_info.race_actual
                player_2_race = info.player_info[1].player_info.race_actual

                match_up = str(player_1_race) + "v" + str(player_2_race)
                match_up = match_up.replace("1", "T").replace("2", "Z").replace("3", "P")

                if len(MATCH_UPS) > 0:
                    if match_up not in MATCH_UPS:
                        print(f"Match-up {match_up} is not in {MATCH_UPS}")
                        continue 

                ## Extracting map information
                map_doc = {}
                map_doc["name"] = info.map_name
                map_doc["starting_location"] = {}


                # Running the replay for each player
                for player_info in info.player_info:
                    player_id = player_info.player_info.player_id
                    replay_id = replay_file.name
                    replay_name = str(replay_file)

                    # Extracting info from replays for a player
                    states, actions, scores, minimap, starting_location = extract_all_info_once(controller, replay_data, map_data, player_id)

                    for key in minimap:
                        map_doc[key] = minimap[key]

                    map_doc["starting_location"][f"player_{player_id}"] = starting_location

                    result = None
                    if player_info.player_result.result == 1:
                        result = 1
                    elif player_info.player_result.result == 2:
                        result = -1
                    else:
                        result = 0

                    player_doc = {
                        "replay_name": replay_name,
                        "replay_id": replay_id,
                        "player_id": player_id,
                        "player_mmr": info.player_info[player_id - 1].player_mmr,
                        "player_apm": info.player_info[player_id - 1].player_apm,
                        "race": str(player_info.player_info.race_actual)
                        .replace("1", "T")
                        .replace("2", "Z")
                        .replace("3", "P"),
                        "result": result
                    }

                    states_documents = []
                    for frame in states:
                        state_doc = {
                            "replay_name": replay_name,
                            "replay_id": replay_id,
                            "player_id": player_id,
                            "frame_id": int(frame),
                            **states[frame]
                        }
                        states_documents.append(state_doc)

                    actions_documents = [{
                                    "replay_name": replay_name,
                                    "replay_id": replay_id,
                                    "player_id": player_id,
                                    "frame_id": int(frame),
                                    "actions": actions[frame]
                                } for frame in actions]

                    scores_documents = []
                    for frame in scores:
                        score_doc = {
                            "replay_name": replay_name,
                            "replay_id": replay_id,
                            "player_id": player_id,
                            "frame_id": int(frame),
                            **scores[frame]
                        }
                        scores_documents.append(score_doc)

                    players_collection.insert(player_doc)
                    states_collection.insert_many(states_documents)
                    actions_collection.insert_many(actions_documents)
                    scores_collection.insert_many(scores_documents)

                replay_doc = {
                    "replay_name": replay_name,
                    "replay_id": replay_id,
                    "match_up": match_up,
                    "game_duration_loops": info.game_duration_loops,
                    "game_duration_seconds": info.game_duration_seconds,
                    "game_version": info.game_version,
                    "map": map_doc,
                }

                replays_collection.insert(replay_doc)
                print(f"Successfully filled all collections of replay {replay_id}")
    except Exception as e: # Add the exception to be the protocol error.
        client.close()        
        print(f"Replay {last_replay_processed.name} seems to be closing the connection. Exception: {e}")
        process_replays(replay_files, run_config, last_replay_processed=last_replay_processed)

def ingest(replay_files):
    run_config = run_configs.get()
    # They wrap this in a try-except.
    process_replays(replay_files, run_config)

# if __name__ == '__main__':
#     pass