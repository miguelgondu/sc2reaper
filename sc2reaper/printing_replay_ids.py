import pymongo

client = pymongo.MongoClient()
db = client.replays_database_TvZ

# for coll in db.list_collections():
# 	print(coll)

replays = db.replays

for replay_doc in replays.find({}, {'replay_id': 1}):
	print(replay_doc["replay_id"])
