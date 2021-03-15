def get_score(observation):
    """
    This function returns a dict "score", holding:
        - the mineral and vespene collection rate in score["collection_rate"]
        - idle worker time in score["idle_worker_time"]
        - killed minerals in score["killed_minerals"]
        - killed vespene in score["killed_vespene"]
        - used minerals in score["used_minerals"]
        - used vespene in score["used_vespene"]

    It is highly customizable, feel free to add anything you'd like
    to track in score. To see which things are defined in the score
    observations, feel free to print score_obs (or obs.score).
    """
    score = {}
    
    score_obs = observation.score.score_details    

    score["collection_rate"] = {
        "minerals": score_obs.collection_rate_minerals,
        "vespene": score_obs.collection_rate_vespene,
    }

    score["idle_worker_time"] = score_obs.idle_worker_time
    score["idle_production_time"] = score_obs.idle_production_time

    score["killed_minerals"] = {
        "none": score_obs.killed_minerals.none,
        "army": score_obs.killed_minerals.army,
        "economy": score_obs.killed_minerals.economy,
        "technology": score_obs.killed_minerals.technology,
        "upgrade": score_obs.killed_minerals.upgrade,
    }

    score["killed_vespene"] = {
        "none": score_obs.killed_vespene.none,
        "army": score_obs.killed_vespene.army,
        "economy": score_obs.killed_vespene.economy,
        "technology": score_obs.killed_vespene.technology,
        "upgrade": score_obs.killed_vespene.upgrade,
    }

    score["used_minerals"] = {
        "none": score_obs.used_minerals.none,
        "army": score_obs.used_minerals.army,
        "economy": score_obs.used_minerals.economy,
        "technology": score_obs.used_minerals.technology,
        "upgrade": score_obs.used_minerals.upgrade,
    }

    score["used_vespene"] = {
        "none": score_obs.used_vespene.none,
        "army": score_obs.used_vespene.army,
        "economy": score_obs.used_vespene.economy,
        "technology": score_obs.used_vespene.technology,
        "upgrade": score_obs.used_vespene.upgrade,
    }

    return score
