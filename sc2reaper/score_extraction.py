from encoder import encoder
enc = encoder()
e = lambda x: 'e' + str(enc[x])

def get_score(observation):
    '''
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
    '''
    score = {}

    score_obs = observation.score.score_details

    # print(f"dir(score_obs): {dir(score_obs)}")
    # print(f"score_obs: {score_obs}")

    score[e("collection_rate")] = {
        e("minerals"): score_obs.collection_rate_minerals,
        e("vespene"): score_obs.collection_rate_vespene,
    }

    score[e("idle_worker_time")] = score_obs.idle_worker_time

    score[e("killed_minerals")] = {
        e('none'): score_obs.killed_minerals.none,
        e('army'): score_obs.killed_minerals.army,
        e('economy'): score_obs.killed_minerals.economy,
        e('technology'): score_obs.killed_minerals.technology,
        e('upgrade'): score_obs.killed_minerals.upgrade,
    }

    score[e("killed_vespene")] = {
        e('none'): score_obs.killed_vespene.none,
        e('army'): score_obs.killed_vespene.army,
        e('economy'): score_obs.killed_vespene.economy,
        e('technology'): score_obs.killed_vespene.technology,
        e('upgrade'): score_obs.killed_vespene.upgrade,
    }

    score[e("used_minerals")] = {
        e('none'): score_obs.used_minerals.none,
        e('army'): score_obs.used_minerals.army,
        e('economy'): score_obs.used_minerals.economy,
        e('technology'): score_obs.used_minerals.technology,
        e('upgrade'): score_obs.used_minerals.upgrade,
    }

    score[e("used_vespene")] = {
        e('none'): score_obs.used_vespene.none,
        e('army'): score_obs.used_vespene.army,
        e('economy'): score_obs.used_vespene.economy,
        e('technology'): score_obs.used_vespene.technology,
        e('upgrade'): score_obs.used_vespene.upgrade,
    }

    return score
