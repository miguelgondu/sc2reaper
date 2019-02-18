import pymongo

client = pymongo.MongoClient()
db = client.replays_database

# for coll in db.list_collections():
# 	print(coll)

replays = db.replays
players = db.players
states = db.states
actions = db.actions
scores = db.scores

replays.create_index("replay_id")
players.create_index("replay_id")
states.create_index([("replay_id", pymongo.ASCENDING), ("frame_id", pymongo.ASCENDING)])
actions.create_index([("replay_id", pymongo.ASCENDING), ("frame_id", pymongo.ASCENDING)])
scores.create_index([("replay_id", pymongo.ASCENDING), ("frame_id", pymongo.ASCENDING)])

# Getting all replay ids.
replay_ids = []
for replay_doc in replays.find({}, {'replay_id': 1}):
	replay_ids.append(replay_doc["replay_id"])

# Getting all apms from all replays.
players_apm = {}
for replay_id in replay_ids:
	players_apm[replay_id] = {}
	for player_id in [1, 2]:
		cursor = players.find({'replay_id': replay_id, 'player_id': player_id})
		for player_doc in cursor:
			players_apm[replay_id][player_id] = player_doc["player_apm"]


# Getting all supply for a single replay for a single player
replay_1 = replay_ids[-1]
for state in states.find({"replay_id": replay_1, "player_id": 1}).sort("frame_id", 1):
	print(f'frame: {state["frame_id"]}, supply: {state["supply"]}')


# Getting all state-action-score triplets.
def get_frames(replay_id):
	frames = []
	for score in scores.find({'replay_id': replay_id}):
		frames.append(score["frame_id"])

	return frames

states_list = []
actions_list = []
scores_list = []
for replay_id in replay_ids:
	frames = get_frames(replay_id)
	for frame in frames:
		print(f"quering frame {frame} for replay {replay_id}")
		condition = {"replay_id": replay_id, "frame_id": frame}
		for action in actions.find({"replay_id": replay_id, "frame_id": str(frame)}):
			actions_list.append(action)
		for state in states.find(condition):
			states_list.append(state)
		for score in scores.find(condition):
			scores_list.append(score)

print(list(zip(states_list, actions_list, scores_list))[10])

# print(f"states list: {states_list}")
# print(f"actions list: {actions_list}")
# print(f"scores list: {scores_list}")
# print(f"state: {states_list[10]}, action: {actions_list[10]}, score: {scores_list[10]}")
