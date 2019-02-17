from pymongo import MongoClient

client = MongoClient()
db = client.replays_database
replays = db.replays

for replay in replays.find():
	print(replay["replay_id"], replay["match_up"])

# for state in states.find({'replay_name': "/home/mgd/StarCraftII/Replays/3f9e30f72c11d74d5616d813ee040de28e41269280b658b61af0e48211c8f43c.SC2Replay", "player_id": 1}, {"supply":1, "frame_id":1}).sort("frame_id", 1): 
# 	print() 
#     print(state)   
