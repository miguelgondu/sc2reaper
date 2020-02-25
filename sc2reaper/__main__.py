"""Package as standalone usable sc2reaper."""
import sys
import multiprocessing as mp
import os
import glob
import pymongo
import json

from sc2reaper.sc2reaper import ingest as _ingest
from sc2reaper.sc2reaper import DB_NAME
from sc2reaper import utils

with open(str(__file__).replace('__main__.py', 'config.json')) as fp:
    doc = json.load(fp)
    sc2_path = doc["SC2_PATH"]

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

    # If the database already exists, we check if we have already
    # processed some of the replays, and substract them from the
    # set we want to process. That way, we don't process replays twice.
    client = pymongo.MongoClient()
    if DB_NAME in client.list_database_names():
        db = client[DB_NAME]
        replays = db["replays"]

    if path_to_replays.endswith(".SC2Replay"):
        # it's actually just a replay.
        replay_files = [path_to_replays]
    else:
        replay_files = glob.glob(f"{path_to_replays}/*.SC2Replay")

    if DB_NAME in client.list_database_names():
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
    ingest(argv[1], argv[2])
