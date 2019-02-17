"""Main module."""

import gzip
import json
import multiprocessing

from google.protobuf.json_format import MessageToDict
from pymongo import MongoClient
from pysc2 import run_configs
from pysc2.lib import features, point
from pysc2.lib.protocol import ProtocolError
from s2clientprotocol import sc2api_pb2 as sc_pb

from sc2reaper.encoder import encode
from sc2reaper.action_extraction import get_actions, get_human_name
from sc2reaper.score_extraction import get_score
from sc2reaper.state_extraction import get_state
from sc2reaper.unit_extraction import get_unit_doc

STEP_MULT = 24
size = point.Point(64, 64)
interface = sc_pb.InterfaceOptions(
    raw=True, score=True, feature_layer=sc_pb.SpatialCameraSetup(width=24)
)

size.assign_to(interface.feature_layer.resolution)
size.assign_to(interface.feature_layer.minimap_resolution)


def extract_action_frames(controller, replay_data, map_data, player_id):
    """
    This function runs through the replay once and extracts no-ops and a list
    of frames in which macro actions started being taken. This list is then 
    used in another function that runs through the replay another time and 
    considers only those positions.
    """
    controller.start_replay(
        sc_pb.RequestStartReplay(
            replay_data=replay_data,
            map_data=map_data,
            options=interface,
            observed_player_id=player_id,
        )
    )

    abilities = controller.data_raw().abilities
    units_raw = controller.data_raw().units
    obs = controller.observe()

    # print(f"raw units: {obs.observation.raw_data.units}")

    # Extracting map information
    height_map_minimap = obs.observation.feature_layer_data.minimap_renders.height_map
    starting_location = None
    for unit in obs.observation.raw_data.units:
        unit_doc = get_unit_doc(unit)
        # print(f'unit name : {units_raw[unit_doc["unit_type"]].name}')
        if units_raw[unit_doc["unit_type"]].name in [
            "CommandCenter",
            "Nexus",
            "Hatchery",
        ]:
            # print(f"I found a {units_raw[unit_doc['unit_type']].name}!")
            if unit.alliance == 1:
                starting_location = unit_doc["location"]
                break

    try:
        assert starting_location != None
    except AssertionError:
        print("Wasn't able to determine a player's starting locations, weird")

    map_doc_local = {"minimap": {"height_map": MessageToDict(height_map_minimap)}}

    no_ops_actions = (
        {}
    )  # a dict of action dics which is to be merged to actual macro actions.
    no_ops_states = {}
    no_ops_scores = {}
    macro_action_frames = (
        []
    )  # a list that will hold the frames in which macro actions START to take place. i.e. the left limit of the time interval.

    # Initialization of docs.
    initial_frame = obs.observation.game_loop

    new_actions = get_actions(obs, abilities)
    # print("I MEAN, THIS SHOULD BE PRINTED ALWAYS")
    no_ops_states[str(initial_frame)] = get_state(obs.observation, initial_frame)
    no_ops_actions[str(initial_frame)] = new_actions
    no_ops_scores[str(initial_frame)] = get_score(obs.observation)

    # running through the replay
    while True:
        try:
            controller.step(STEP_MULT)
            obs = controller.observe()
            frame_id = obs.observation.game_loop

            new_actions = get_actions(obs, abilities)
            if len(new_actions) == 0:
                # i.e. no op
                no_ops_states[str(frame_id)] = get_state(obs.observation, frame_id)
                no_ops_actions[str(frame_id)] = new_actions
                no_ops_scores[str(frame_id)] = get_score(obs.observation)
            if len(new_actions) > 0:
                # print("one or more macro actions was found")
                macro_action_frames.append(frame_id - STEP_MULT)

        except ProtocolError:
            obs = controller.observe()
            print(f"last frame recorded: {obs.observation.game_loop}")
            break

    return (
        no_ops_states,
        no_ops_actions,
        no_ops_scores,
        macro_action_frames,
        map_doc_local,
        starting_location,
    )


def extract_macro_actions(
    controller, replay_data, map_data, player_id, macro_action_frames
):
    """
    This function takes macro_action_frames and moves through the replay only considering the places
    in which macro actions took place.
    """
    controller.start_replay(
        sc_pb.RequestStartReplay(
            replay_data=replay_data,
            map_data=map_data,
            options=interface,
            observed_player_id=player_id,
        )
    )

    obs = controller.observe()
    abilities = controller.data_raw().abilities

    # a dict of action dics which is to be merged to the other no-ops actions.
    macro_actions = {}
    macro_states = {}
    macro_scores = {}
    past_frame = obs.observation.game_loop

    for frame in macro_action_frames:
        if past_frame == 0:
            controller.step(frame - past_frame)
        else:
            controller.step(
                frame - past_frame - 1
            )
        obs = controller.observe()
        assert obs.observation.game_loop == frame

        for _ in range(STEP_MULT):
            obs = controller.observe()
            frame_id = obs.observation.game_loop

            new_actions = get_actions(obs, abilities)
            if len(new_actions) > 0:
                # i.e. if they're not no-ops:
                macro_states[str(frame_id)] = get_state(
                    obs.observation, frame_id
                )  # with this revamp, frame_id is unnecessary here.
                macro_actions[str(frame_id)] = new_actions  # storing the whole list.
                macro_scores[str(frame_id)] = get_score(obs.observation)

            controller.step(1)

        past_frame = obs.observation.game_loop

    return macro_states, macro_actions, macro_scores


def ingest(replay_file):
    run_config = run_configs.get()

    with run_config.start() as controller:
        print(f"Processing replay {replay_file}")
        replay_data = run_config.replay_data(replay_file)
        info = controller.replay_info(replay_data)

        map_data = None
        if info.local_map_path:
            map_data = run_config.map_data(info.local_map_path)

        # print(f"replay info: {info}")
        # Mongo experiments
        client = MongoClient("localhost", 27017)
        db = client["replays_example_4"]
        # replay_collection = db["replays"]

        # Extracting general information for the replay document

        ## Extracting the Match-up

        player_1_race = info.player_info[0].player_info.race_actual
        player_2_race = info.player_info[1].player_info.race_actual

        match_up = str(player_1_race) + "v" + str(player_2_race)
        match_up = match_up.replace("1", "T").replace("2", "Z").replace("3", "P")

        # replay_doc = {
        #     e('replay_name'): replay_file,
        #     e('match_up'): match_up,
        #     e('game_duration_loops'): info.game_duration_loops,
        #     e('game_duration_seconds'): info.game_duration_seconds,
        #     e('game_version'): info.game_version
        # }

        map_doc = {}
        map_doc["starting_location"] = {}

        for player_info in info.player_info:
            # print(player_info)
            player_id = player_info.player_info.player_id
            collection_name = replay_file.split("/")[-1]
            collection_name = collection_name.split(".")[0] + f"_{player_id}"
            player_collection = db[collection_name]
            # print(f"player info for player {player_id}: {player_info}")
            # Storing map information

            # Extracting info from replays
            no_ops_states, no_ops_actions, no_ops_scores, macro_action_frames, map_doc_local, starting_location = extract_action_frames(
                controller, replay_data, map_data, player_id
            )
            macro_states, macro_actions, macro_scores = extract_macro_actions(
                controller, replay_data, map_data, player_id, macro_action_frames
            )

            for key in map_doc_local:
                map_doc[key] = map_doc_local[key]

            map_doc["starting_location"][f"player_{player_id}"] = starting_location

            # Merging both
            states = {**no_ops_states, **macro_states}
            actions = {**no_ops_actions, **macro_actions}
            scores = {**no_ops_scores, **macro_scores}

            result = None
            if player_info.player_result.result == 1:
                result = 1
            elif player_info.player_result.result == 2:
                result = -1
            else:
                result = 0

            # player_doc = {
            #     e('player_id'): player_id,
            #     e('race'): str(player_info.player_info.race_actual).replace("1", "T").replace("2", "Z").replace("3", "P"),
            #     e('result'): result,
            #     e('states'): states,
            #     e('actions'): actions,
            #     e('scores'): scores
            # }

            player_info_doc = {
                "replay_name": replay_file,
                "player_id": player_id,
                "match_up": match_up,
                "game_duration_loops": info.game_duration_loops,
                "game_duration_seconds": info.game_duration_seconds,
                "game_version": info.game_version,
                "race": str(player_info.player_info.race_actual)
                .replace("1", "T")
                .replace("2", "Z")
                .replace("3", "P"),
                "result": result,
            }

            players_collection
            states_collection
            actions_collection
            scores_collection

            player_collection.insert_many(
                encode([player_info_doc, states, actions, scores])
            )
            print(f"Successfully filled replay collection {collection_name}")
