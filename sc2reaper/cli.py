"""Console script for sc2reaper."""
import sys
import click


@click.group()
def main(args=None):
    """SC2 Reaper command line tools"""
    return 0


@main.command()
@click.argument("files", nargs=-1, type=click.File("r"))
@click.option("--mongo-url", "-m", type=str, default=None, help="MongoDB URL.")
def ingest(files, mongo_url):
    """
    Load a few replays into a mongo database.
    """
    click.echo(f"Storing replays in {mongo_url}")
    for _file in files:
        click.echo(_file.name)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
