import unit_extraction
import resources_extraction
import supply_extraction

from encoder import encode

def get_state(observation, frame_id):
    '''
    This function returns a state, defined as a dict holding
        - a frame counter
        - the actual frame being recorded
        - resources of the player
        - supply
        - allied units (under the key "units")
        - allied units in progress (in "units_in_progress")
        - visible enemy units
        - seen enemy units (i.e. all the ones I have seen in the past).
    '''

    # Creating the state
    state = {}

    state["frame_id"] = frame_id # a.k.a game loop (or something similar when multiple actions are being stored)

    state["resources"] = encode({
        "minerals": resources_extraction.get_minerals(observation),
        "vespene": resources_extraction.get_vespene(observation)
    })
    
    state["supply"] = encode({
        "used": supply_extraction.get_used_supply(observation),
        "total": supply_extraction.get_total_supply(observation),
        "army": supply_extraction.get_army_supply(observation),
        "workers": supply_extraction.get_worker_supply(observation)
    })

    allied_units = unit_extraction.get_allied_units(observation) # holds unit docs.
    unit_types = [unit["unit_type"] for unit in allied_units]

    state["units"] = {
        str(unit_type): [u for u in allied_units if u["unit_type"] == unit_type] for unit_type in unit_types
    }

    # Units in progress
    state["units_in_progress"] = {}
    units_in_progress = unit_extraction.get_allied_units_in_progress(observation)
    for unit_type, unit_tag in units_in_progress:
        if str(unit_type) not in state["units_in_progress"]:
            state["units_in_progress"][str(unit_type)] = {str(unit_tag): units_in_progress[unit_type, unit_tag]}
        else:
            state["units_in_progress"][str(unit_type)][str(unit_tag)] = units_in_progress[unit_type, unit_tag]

    state["units_in_progress"] = encode(state["units_in_progress"])


    # Visible enemy units (enemy units on screen)
    visible_enemy_units = unit_extraction.get_visible_enemy_units(observation)
    state["visible_enemy_units"] = {str(unit_type): visible_enemy_units[unit_type] for unit_type in visible_enemy_units}

    # Seen enemy units
    # if frame_id == 1: # this is a hot-fix, fix it properly.
    #     state["seen_enemy_units"] = {}
    # else:
    #     seen_enemy_units = unit_extraction.get_seen_enemy_units(observation, last_state)
    #     state["seen_enemy_units"] = {str(unit_type): seen_enemy_units[unit_type] for unit_type in seen_enemy_units}

    return encode(state)
