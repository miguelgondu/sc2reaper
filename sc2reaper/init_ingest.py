import pymongo
import multiprocessing as mp

from pathlib import Path
from sc2reaper.sc2reaper import ingest as _ingest
from sc2reaper.sc2reaper import DB_NAME, address, port_num
from sc2reaper import utils


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
        replay_files = [replay for replay in path_to_replays.glob("*.SC2Replay")]

    # If the database already exists, we check if we have already
    # processed some of the replays, and substract them from the
    # set we want to process. That way, we don't process replays twice.
    client = pymongo.MongoClient(address, port_num)
    if DB_NAME in client.list_database_names():
        db = client[DB_NAME]
        replays = db["replays"]
        parsed_files = set([
            Path(doc['replay_name']) for doc in replays.find()
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
        raise ValueError("Found no new replays in path. Do they end on SC2Replay?")
