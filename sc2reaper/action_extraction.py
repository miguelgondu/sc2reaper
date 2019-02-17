from sc2reaper.encoder import encode


def is_macro_action(unit_command_action, abilities):
    """
	This function determines if a unit_command action is a macro action
	based on the following criteria: if the action is related to training, morphing,
	researching or building units or technologies, then it is a macro action. It 
	returns a boolean.

	Feel free to add more stuff in macro_names by checking the stableid.json and
	adding names that you feel should be stored as macro actions.
	"""
    macro_names = [
        "Morph",
        "Research",
        "Train",
        "ZergBuild",
        "ProtossBuild",
        "TerranBuild",
    ]

    for name in macro_names:
        ability = abilities[unit_command_action.ability_id]
        # print(f"ability: {ability}")
        if name in ability.link_name:
            # we're also storing the the canceling of stuff.
            # if hasattr(ability, 'button_name') and 'Cancel' in ability.button_name:
            # 	return False
            return True

    return False


def get_human_name(action_doc, abilities):
    ability = abilities[action_doc["ability_id"]]
    return str(ability.link_name) + str(ability.button_name)


def get_actions(obs, abilities):
    """
	This function is supposed to return macro actions from an observation.

	Arguments:
		-obs, an observation taken from a obs =  controller.observe()
		-abilities, which is the result of controller.raw_data().abilities

	Returns:
		- a list macro_actions of all the macro actions found in obs.actions.

	Raw observations and unit commands are defined in the protocol here:
	https://github.com/Blizzard/s2client-proto/blob/aa41daa2da79431d3b88b115e6a17b23a9260529/s2clientprotocol/raw.proto#L160

	TO-DO:
		- clean the hasattr, it seems to be innecesary
	"""

    actions = obs.actions
    macro_actions = []
    for action in actions:
        if hasattr(action, "action_raw") and hasattr(action.action_raw, "unit_command"):
            if is_macro_action(action.action_raw.unit_command, abilities):
                action_doc = {}
                if hasattr(action.action_raw.unit_command, "ability_id"):
                    action_doc["ability_id"] = action.action_raw.unit_command.ability_id
                if hasattr(action.action_raw.unit_command, "unit_tags"):
                    action_doc["unit_tags"] = [
                        tag for tag in action.action_raw.unit_command.unit_tags
                    ]
                if hasattr(action.action_raw.unit_command, "target_unit_tag"):
                    action_doc[
                        "target_unit_tag"
                    ] = action.action_raw.unit_command.target_unit_tag
                if hasattr(action.action_raw.unit_command, "target_world_space_pos"):
                    action_doc["target_world_space_pos"] = {
                        "x": action.action_raw.unit_command.target_world_space_pos.x,
                        "y": action.action_raw.unit_command.target_world_space_pos.y,
                    }
                macro_actions.append(encode(action_doc))
    return macro_actions

