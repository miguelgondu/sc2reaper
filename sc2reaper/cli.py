"""Console script for sc2reaper."""
import sys
import click
import multiprocessing as mp
import os
import glob

from sc2reaper import sc2reaper
from sc2reaper import utils

os.environ["SC2PATH"] = "/media/mgd/DATA/StarCraft2_4_0_2/StarCraftII"

@click.group()
def main(args=None):
    """SC2 Reaper command line tools"""
    return 0


@main.command()
@click.argument("path_to_replays", type=str)
@click.option("--proc", type=int, default=1, help="Amount of processors you want to devote.")
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

    if path_to_replays.endswith(".SC2Replay"):
        # it's actually just a replay.
        replay_files = [path_to_replays]
    else:
        replay_files = glob.glob(f"{path_to_replays}/*.SC2Replay")

    # TODO: split this list in multiple queues and set up a multiprocess.
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
