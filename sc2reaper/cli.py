"""Console script for sc2reaper."""
import sys
import click
import multiprocessing as mp

from sc2reaper import sc2reaper
from sc2reaper import utils

@click.group()
def main(args=None):
    """SC2 Reaper command line tools"""
    return 0


@main.command()
@click.argument("path_to_replays", type=str)
@click.option("--processes", type=int, default=1, help="Amount of processors you want to devote.")
def ingest(path_to_replays, processes):
    """
    Load a replay into a mongo database.
    """
    # So that pysc2 runs:
    from absl import flags
    import sys

    FLAGS = flags.FLAGS
    FLAGS(sys.argv)

    if path_to_replays.endswith(".SC2Replay"):
        replay_files = [path_to_replays]
    else:
        replay_files = glob.glob(f"{path_to_replays}/*.SC2Replay")

    # TODO: split this list in multiple queues and set up a multiprocess.
    replay_files_chunks = utils.split(replay_files, processes)

    # Ingesting the replay
    with mp.Pool(processes) as p:
        p.map(sc2reaper.ingest, replay_files_chunks)
    
    # sc2reaper.ingest(path_to_replays)

if __name__ == "__main__":
    main()  # pragma: no cover
