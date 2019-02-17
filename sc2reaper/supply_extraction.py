def get_used_supply(observation):
    return observation.player_common.food_used


def get_total_supply(observation):
    return observation.player_common.food_cap


def get_army_supply(observation):
    return observation.player_common.food_army


def get_worker_supply(observation):
    return observation.player_common.food_workers
