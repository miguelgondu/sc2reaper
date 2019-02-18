import pymongo

client = pymongo.MongoClient()
db = client.replays_database

replays = db.replays
players = db.players

csv_file = "replay_id, player_id, player_mmr, player_apm, result\n"

replay_ids = []
for replay in replays.find({}, {"replay_id": 1}):
	replay_ids.append(replay["replay_id"])


for replay_id in replay_ids:
	for player in players.find({"replay_id": replay_id}):
		line = f"{replay_id},"
		line += f"{player['player_id']},"
		line += f"{player['player_mmr']},"
		line += f"{player['player_apm']},"
		line += f"{player['result']}\n"
		csv_file += line

with open('mmr_apm_table.csv', 'w') as output:
	output.write(csv_file)
