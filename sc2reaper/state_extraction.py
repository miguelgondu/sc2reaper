from sc2reaper import unit_extraction
from sc2reaper import resources_extraction
from sc2reaper import supply_extraction


def get_state(observation):
    """
    This function returns a state, defined as a dict holding
        - a frame counter
        - the actual frame being recorded
        - resources of the player
        - supply
        - allied units (under the key "units")
        - allied units in progress (in "units_in_progress")
        - visible enemy units
        - seen enemy units (i.e. all the ones I have seen in the past).

    Recall that the observation object is defined here:
    https://github.com/deepmind/pysc2/blob/master/docs/environment.md#structured

    Yet, we heavily encourage just printing it to get a sense of what's inside.
    Since we're dealing with replays instead of games, the observations and
    the name of their attributes change.
    """

    # Creating the state
    state = {}

    # a.k.a game loop (or something similar when multiple actions are being stored)
    state["resources"] = {
        "minerals": resources_extraction.get_minerals(observation),
        "vespene": resources_extraction.get_vespene(observation),
    }

    state["supply"] = {
        "used": supply_extraction.get_used_supply(observation),
        "total": supply_extraction.get_total_supply(observation),
        "army": supply_extraction.get_army_supply(observation),
        "workers": supply_extraction.get_worker_supply(observation),
        "idle_workers": supply_extraction.get_idle_worker_count(observation)
    }

    allied_units = unit_extraction.get_allied_units(observation)  # holds unit docs.
    unit_types = [unit["unit_type"] for unit in allied_units]

    state["units"] = {
        str(unit_type): [u for u in allied_units if u["unit_type"] == unit_type]
        for unit_type in unit_types
    }

    # Units in progress
    
    ## Adding buildings in progress
    state["units_in_progress"] = {}
    units_in_progress = unit_extraction.get_allied_units_in_progress(observation)
    for unit_type, unit_tag in units_in_progress:
        if str(unit_type) not in state["units_in_progress"]:
            state["units_in_progress"][str(unit_type)] = {
                str(unit_tag): units_in_progress[unit_type, unit_tag]
            }
        else:
            state["units_in_progress"][str(unit_type)][
                str(unit_tag)
            ] = units_in_progress[unit_type, unit_tag]


    # Visible enemy units (enemy units on screen)
    visible_enemy_units = unit_extraction.get_visible_enemy_units(observation)
    state["visible_enemy_units"] = {
        str(unit_type): visible_enemy_units[unit_type]
        for unit_type in visible_enemy_units
    }

    state["upgrades"] = [upgrade for upgrade in observation.raw_data.player.upgrade_ids]

    return state
