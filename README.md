sc2reaper
==========

[![image](https://img.shields.io/pypi/v/sc2reaper.svg)](https://pypi.python.org/pypi/sc2reaper)

[![image](https://img.shields.io/travis/miguelgondu/sc2reaper.svg)](https://travis-ci.org/miguelgondu/sc2reaper)

[![Documentation Status](https://readthedocs.org/projects/sc2reaper/badge/?version=latest)](https://sc2reaper.readthedocs.io/en/latest/?badge=latest)

sc2reaper is a tool for extracting data from SC2 replays using [pysc2](https://github.com/deepmind/pysc2) and heavily inspired in [MSC](https://github.com/wuhuikai/MSC). It is intended to be used **as a template** that you can modify in order to extract exactly what you want from replays and how you want it.

-   Free software: MIT license.

Features
--------

-   Digest multiple SC2 replay files into a MongoDB database.

Installation
------------

As a pre-requisite, this installation tutorial assumes that you have [a working installation of pysc2](https://github.com/deepmind/pysc2#quick-start-guide) and that you have already installed [MongoDB](https://docs.mongodb.com/manual/installation/).

First, start by cloning this repo:

```
git clone https://github.com/miguelgondu/sc2reaper.git
```

Second, go to the sc2reaper folder you just cloned using

```
cd sc2reaper
```

Then install the command-line tool using

```
pip install -e .
```

Now you're ready to use `sc2reaper` as a command-line tool! But be careful, in order to extract the information you need, you will need to change some default values in the code itself. Notice that, by running the installation with `-e`, you can modify the code without having to install it every time.

Usage
-----

0. [Set up a `mongod` instance](https://docs.mongodb.com/manual/tutorial/install-mongodb-enterprise-on-ubuntu/#start-mongodb) running in the default port (or at any port, but remember to change the url in the code itself).
1. You will need to change some of the global default values that indicate which replays to store and how to store them. These global values are specified in the `config.json` file you will find inside the sc2reaper folder. It should contain:
	- `DB_NAME`: the name of the database you want to create or update.
	- `STEP_MULT`: the amount of frames per step. For example, setting it to 22 means that you will gather data for (roughly) every second of the replay.
	- `MATCH_UPS`: a list of the match-ups you're interested in. Write it as "TvZ" and "ZvT" if you want, for example, to include all the matches with one Terran player and one Zerg player. Leave it empty to consider all match-ups.
	- `SC2_PATH`: the path to the StarCraftII folder.
	- `PORT_ADDRESS`: the address of the port of the `mongod` instance (by default `localhost`).
	- `PORT_NUMBER`: the number of the port of the `mongod` instance (by default 27017).
2. You should be ready to run `sc2reaper ingest path_to_replay_files --proc=n` or `python -m sc2reaper path_to_replays n`, where `n` is the amount of processors that you want to devote to the process. This ingest function will look for all the files that end in ".SC2Replay" using `glob`. You can also pass the path to a single .SC2Replay file.

After the process ends, the data should be stored in your mongo database.

Usage of the database
---------------------

After ingesting the replays you want to process, you will have a database stored in the path in which your `mongod` was storing the data. [This documentation](https://github.com/miguelgondu/sc2reaper/blob/master/using_sc2reaper_database.md) shows how the default database is constructed and how you can use pymongo to extract relevant information. 

Future work (coming soon)
-------------------------

- Implementing a tool to extract the information as json files.


Credits
-------

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
project template.
