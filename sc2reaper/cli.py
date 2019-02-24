"""Console script for sc2reaper."""
import sys
import click 

from sc2reaper import sc2reaper


@click.group()
def main(args=None):
    """SC2 Reaper command line tools"""
    return 0


@main.command()
@click.argument("file", nargs=1, type=click.File("r"))
# @click.option("--mongo-url", "-m", type=str, default=None, help="MongoDB URL.")
def ingest(file):
    """
    Load a replay into a mongo database.
    """
    # So that pysc2 runs:
    from absl import flags
    import sys

    FLAGS = flags.FLAGS
    FLAGS(sys.argv)

    # Ingesting the replay
    sc2reaper.ingest(file.name)

if __name__ == "__main__":
    main()  # pragma: no cover
