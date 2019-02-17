'''
If I want to truly optimize the process, I should be running the for in observation.raw_data.units only once!

It's a trade-off between modularity and running time. Doing it all in one for would be very spaghetti.

TO-DO: should I do everything using unit docs?, as it is, it mixes actual units (the outputs of
	   observation.raw_data.units) with unit docs, using both of them instead of just one.
'''
from encoder import encoder
enc = encoder()
e = lambda x: 'e' + str(enc[x])

def get_unit_doc(unit):
	return { #TO-DO: add human name.
		e("tag"): unit.tag,
		e("unit_type"): unit.unit_type,
		e("alliance"): unit.alliance,
		e("type"): unit.unit_type,
		e("location"): {'x': unit.pos.x, 'y': unit.pos.y, 'z': unit.pos.z},
		e("owner"): unit.owner,
		e("health"): unit.health,
		e("health_max"): unit.health_max,
		e("shield"): unit.shield,
		e("shield_max"): unit.shield_max,
		e("energy"): unit.energy,
		e("energy_max"): unit.energy_max,
		e("build_progress"): unit.build_progress,
		e("is_on_screen"): unit.is_on_screen
	}

def get_all_units(observation):
	'''
	This function takes an observation and returns all units in the field.
	'''
	return [get_unit_doc(unit) for unit in observation.raw_data.units]

def get_allied_units(observation):
	'''
	This function takes an observation and returns all allied units in the field.
	'''
	return [get_unit_doc(unit) for unit in observation.raw_data.units if unit.alliance == 1]

def get_all_enemy_units(observation):
	'''
	This function takes an observation and returns all enemy units in the field.
	'''
	return [get_unit_doc(unit) for unit in observation.raw_data.units if unit.alliance == 4] 

def get_visible_enemy_units(observation, as_list=False, as_dict=True):
	'''
	This function takes an observation and returns a list of the enemy units that are
	on screen and are visible.

	A unit is considered visible if is either visible (in the protos sense) or if it 
	is snapshotted and finished.

	The definition of display_type can be found here:
	https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/raw.proto#L55 
	'''
	if as_list == as_dict:
		raise ValueError("One and only one of as_list and as_dict should be True")

	if as_list == True:
		visible_enemy_units = []
		for unit in observation.raw_data.units:
			if unit.alliance == 4 and unit.is_on_screen:
				if unit.display_type == 1 or (unit.display_type == 2 and unit.build_progress == 1):
					visible_enemy_units.append(get_unit_doc(unit))

	if as_dict == True:
		# TO-DO: fix this one, this is the root of all bugs.
		visible_enemy_units = {}
		for unit in observation.raw_data.units:
			if unit.alliance == 4 and unit.is_on_screen:
				if unit.display_type == 1 or (unit.display_type == 2 and unit.build_progress == 1):
					if str(unit.unit_type) not in visible_enemy_units:
						visible_enemy_units[str(unit.unit_type)] = [get_unit_doc(unit)]
					else: 
						visible_enemy_units[str(unit.unit_type)].append(get_unit_doc(unit))

	return visible_enemy_units

def get_seen_enemy_units(observation, last_seen):
	'''
	This function takes an observation and the last state (i.e. at time t-1).

	It copies this last seen_enemy_units and adds all the units that are currently being seen and
	that haven't been seen before. If a unit is seen to be killed (i.e it was on screen in the last
	frame, but in this frame it isn't and it isn't in the enemy's all unit list, then remove it)

	It returns this new updated copy (i.e. a dictionary).

	TO-DO: 
	- Modify this function to be more fair and less cheaty: a human player doesn't know
	if a unit in screen is new or not, a human player doesn't have access to the tags, nor
	all enemy units.
	- For an LSTM, store only visible units, the network should be able to "remember" 
	shortly which units where alive. Not storing tags should be fine.
	- Test and fix this more thoroughly. (deadline: friday)
	'''

	# Put new seen units

	seen = last_seen.copy()
	# print(f"seen: {seen}")

	visible_enemy_units = get_visible_enemy_units(observation) # {unit type (str): [unit tags (ints)]}
	for str_unit_type in visible_enemy_units:
		if str_unit_type not in seen:
			seen[str_unit_type] = []

		for unit_doc in visible_enemy_units[str_unit_type]:
			if unit_doc not in seen[str_unit_type]:
				# print(f"unit {unit_tag} ({type(unit_tag)}) (of type {unit_type} ({type(unit_type)})) is new!")
				seen[str_unit_type].append(unit_doc)

	# print(f"seen after adding currently visible units: {last_seen}")

	# Remove killed units

	all_enemy_units = get_all_enemy_units(observation) # already returns unit docs.

	for str_unit_type in seen:
		for unit_doc in seen[str_unit_type]:
			if unit_doc not in all_enemy_units:
				# print(f"removing unit {unit_tag} because it was killed.")
				seen[str_unit_type].remove(unit_doc)

	# print(f"seen after removing killed units: {seen}")

	return seen

def get_allied_units_in_progress(observation):
	'''
	This function takes an observation and returns a dictionary holding 
	the current units in progress. This dictionary is built as follows

	units_in_progress = {
		(unit's type, unit's tag): unit's build progress
	}
	for each allied unit that has a build progress of less than 1.
	'''
	units_in_progress = {}
	for unit in observation.raw_data.units:
		if unit.alliance == 1 and unit.build_progress < 1:
			units_in_progress[(unit.unit_type, unit.tag)] = unit.build_progress

	return units_in_progress
