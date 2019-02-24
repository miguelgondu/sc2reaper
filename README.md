sc2reaper
==========

[![image](https://img.shields.io/pypi/v/sc2reaper.svg)](https://pypi.python.org/pypi/sc2reaper)

[![image](https://img.shields.io/travis/miguelgondu/sc2reaper.svg)](https://travis-ci.org/miguelgondu/sc2reaper)

[![Documentation Status](https://readthedocs.org/projects/sc2reaper/badge/?version=latest)](https://sc2reaper.readthedocs.io/en/latest/?badge=latest)

sc2reaper is a tool for extracting data from SC2 replays using [pysc2](https://github.com/deepmind/pysc2) and heavily inspired in [MSC](https://github.com/wuhuikai/MSC). It is intended to be used **as a template** that you can modify in order to extract exactly what you want from replays and how you want it.

**This tool is still in a very raw state, it's WIP.**

-   Free software: MIT license
-   Documentation: <https://sc2reaper.readthedocs.io>. (Not written yet)

Features
--------

-   Digest a single SC2 replay file into MongoDB databases.
- 	Write jsons containing the extracted information from an SC2 replay file. (Not implemented yet)

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
1. You will need to change some of the global default values that indicate which replays to store and how to store them. In particular, go to [`sc2reaper.py`](https://github.com/miguelgondu/sc2reaper/blob/master/sc2reaper/sc2reaper.py) and change
	-	[`MATCH_UPS`](https://github.com/miguelgondu/sc2reaper/blob/1a67e39d5ca43080edfc1ba0122c7338d435d2a4/sc2reaper/sc2reaper.py#L8), which is a list of the match-ups you're interested in. The defaults are "TvZ" and "ZvT". Leave it empty to consider all match-ups.
	- 	[The name of your database in `client["replay_database_name"]`](https://github.com/miguelgondu/sc2reaper/blob/1a67e39d5ca43080edfc1ba0122c7338d435d2a4/sc2reaper/sc2reaper.py#L49). This is the name that the database will have in the `mongod` instance. Also change the url in `client = pymongo.MongoClient(...)` if your `mongod` instance isn't running on the default 27017 port.
2. Change the amount of frames you want to go though in each step by going to [`sweeper.py`](https://github.com/miguelgondu/sc2reaper/blob/master/sc2reaper/sweeper.py) and changing [`STEP_MULT`](https://github.com/miguelgondu/sc2reaper/blob/1a67e39d5ca43080edfc1ba0122c7338d435d2a4/sc2reaper/sweeper.py#L13).
3. You should be ready to run 

```sc2reaper ingest path_to_replay_file.SC2Replay```

After the process ends, the data should be stored in your mongo database.

Usage of the database
---------------------

After ingesting the replays you want to process, you will have a database stored in the path in which your `mongod` was storing the data. [This documentation](https://github.com/miguelgondu/sc2reaper/blob/master/using_sc2reaper_database.md) shows how the default database is constructed and how you can use pymongo to extract relevant information. 

Future work (coming soon)
-------------------------

- Implementing a multiprocess parallelization of data extraction
- Implementing a tool to extract the information as json files.


Credits
-------

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
project template.
