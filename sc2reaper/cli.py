"""Console script for sc2reaper."""
import sys
import click
import multiprocessing as mp
import os
import glob
import pymongo

from sc2reaper import sc2reaper
from sc2reaper import utils

os.environ["SC2PATH"] = "/media/mgd/DATA/StarCraft2_4_1_2/StarCraftII"

@click.group()
def main(args=None):
    """SC2 Reaper command line tools"""
    return 0


@main.command()
@click.argument("path_to_replays", type=str)
@click.option("--proc", type=int, default=1, help="Amount of processors you want to devote.")
@click.option("--db_name", type=str, default=None, help="Name of the database you want to create or update.")
def ingest(path_to_replays, proc, db_name):
    """
    Load a replay into a mongo database.
    """
    # So that pysc2 runs:
    from absl import flags
    import sys
    FLAGS = flags.FLAGS
    flags.DEFINE_integer("proc", 1, "Amount of processors you want to devote.")
    flags.DEFINE_string("db_name", None, "Name of the database you want to create or update.")
    FLAGS(sys.argv)

    if db_name is not None:
        client = pymongo.MongoClient()
        db = client[db_name]
        replays = db["replays"]

    if path_to_replays.endswith(".SC2Replay"):
        # it's actually just a replay.
        replay_files = [path_to_replays]
    else:
        replay_files = set(glob.glob(f"{path_to_replays}/*.SC2Replay"))

    if db_name is not None:
        parsed_files = set([
            doc["replay_name"] for doc in replays.find()
        ])
        print(f"Found {len(parsed_files)} replays in the database already.")

        replay_files -= parsed_files

    if len(replay_files) > 1:
        replay_files_chunks = utils.split(replay_files, proc)

        # Ingesting the replay
        with mp.Pool(proc) as p:
            p.map(sc2reaper.ingest, replay_files_chunks)
    
    elif len(replay_files) == 1:
        sc2reaper.ingest(path_to_replays)

    else:
        raise ValueError("Found no replays in path. Do they end on SC2Replay?")


if __name__ == "__main__":
    main()  # pragma: no cover
