"""
Package as standalone usable sc2reaper.
Usage:
python -m sc2reaper path/to/replays amount_of_processors

Works great if you're running a very particular python executable
somewhere in a server.
"""
import sys
import multiprocessing as mp
import os
import pymongo
import json
import jsonschema

from pathlib import Path
from jsonschema import validate
from sc2reaper.sc2reaper import ingest as _ingest
from sc2reaper.sc2reaper import DB_NAME
from sc2reaper import utils


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
        doc = json.load(fp)
        sc2_path = doc["SC2_PATH"]
        address = doc["PORT_ADDRESS"]
        port = doc["PORT_NUMBER"]
    os.environ["SC2PATH"] = sc2_path

else:
    print("Loading according to default config.json")
    default_config_path =  Path(__file__).parent / 'config.json'
    with default_config_path.open() as fp:
        doc = json.load(fp)
        sc2_path = doc["SC2_PATH"]
        address = doc["PORT_ADDRESS"]
        port = doc["PORT_NUMBER"]
    os.environ["SC2PATH"] = sc2_path

def ingest(path_to_replays, proc):
    """
    Load a replay into a mongo database.
    """
    # So that pysc2 runs:
    from absl import flags
    import sys
    FLAGS = flags.FLAGS
    flags.DEFINE_integer("proc", 1, "Amount of processors you want to devote.")
    FLAGS(sys.argv)

    path_to_replays = Path(path_to_replays)

    if path_to_replays.name.endswith(".SC2Replay"):
        # it's actually just a replay.
        replay_files = [str(path_to_replays)]
    else:
        replay_files = map(str, path_to_replays.glob("*.SC2Replay"))

    # If the database already exists, we check if we have already
    # processed some of the replays, and substract them from the
    # set we want to process. That way, we don't process replays twice.
    client = pymongo.MongoClient(address, port)
    if DB_NAME in client.list_database_names():
        db = client[DB_NAME]
        replays = db["replays"]
        parsed_files = set([
            doc["replay_name"] for doc in replays.find()
        ])
        print(f"Found {len(parsed_files)} replays in the database already.")

        replay_files = set(replay_files)
        replay_files -= parsed_files
        replay_files = list(replay_files)

    client.close()

    if len(replay_files) > 1:
        replay_files_chunks = utils.split(replay_files, proc)

        # Ingesting the replays
        with mp.Pool(proc) as p:
            p.map(_ingest, replay_files_chunks)
    
    elif len(replay_files) == 1:
        _ingest(replay_files)

    else:
        raise ValueError("Found no replays in path. Do they end on SC2Replay?")


if __name__ == "__main__":
    argv = sys.argv
    # print(argv)
    ingest(argv[1], int(argv[2]))
