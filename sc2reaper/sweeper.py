from pysc2.lib import features, point
from pysc2.lib.protocol import ProtocolError
from s2clientprotocol import sc2api_pb2 as sc_pb

from google.protobuf.json_format import MessageToDict

from sc2reaper.action_extraction import get_actions
from sc2reaper.score_extraction import get_score
from sc2reaper.state_extraction import get_state
from sc2reaper.unit_extraction import get_unit_doc
import json

with open(str(__file__).replace('sweeper.py', 'config.json')) as fp:
    doc = json.load(fp)
    STEP_MULT = doc["STEP_MULT"]

size = point.Point(64, 64)
interface = sc_pb.InterfaceOptions(
    raw=True, score=True, feature_layer=sc_pb.SpatialCameraSetup(width=24)
)

size.assign_to(interface.feature_layer.resolution)
size.assign_to(interface.feature_layer.minimap_resolution)

def extract_all_info_once(controller, replay_data, map_data, player_id):
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

    # Extracting map information
    # height_map_minimap = obs.observation.feature_layer_data.minimap_renders.height_map
    starting_location = None
    for unit in obs.observation.raw_data.units:
        unit_doc = get_unit_doc(unit)
        if units_raw[unit_doc["unit_type"]].name in [
            "CommandCenter",
            "Nexus",
            "Hatchery",
        ]:
            if unit.alliance == 1:
                starting_location = unit_doc["location"]
                break

    try:
        assert starting_location != None
    except AssertionError:
        print("Wasn't able to determine a player's starting locations, weird")

    minimap = {"minimap": {"height_map": None}}

    actions = {}  # a dict of action dics which is to be merged to actual macro actions.
    states = {}
    scores = {}

    initial_frame = obs.observation.game_loop

    states[str(initial_frame)] = get_state(obs.observation)
    actions[str(initial_frame)] = get_actions(obs.actions, abilities)
    scores[str(initial_frame)] = get_score(obs.observation)

    # running through the replay
    while True:
        try:
            controller.step(STEP_MULT)
            obs = controller.observe()
            frame_id = obs.observation.game_loop

            states[str(frame_id)] = get_state(obs.observation)
            actions[str(frame_id)] = get_actions(obs.actions, abilities)
            scores[str(frame_id)] = get_score(obs.observation)

        except ProtocolError:
            obs = controller.observe()
            print(f"last frame recorded: {obs.observation.game_loop}")
            break

    return (states, actions, scores, minimap, starting_location)


def extract_action_frames(controller, replay_data, map_data, player_id):
    """
    This function runs through the replay once and extracts no-ops and a list
    of frames in which macro actions started being taken. This list is then 
    used in another function that runs through the replay another time and 
    considers only those positions.

    It isn't being used in the replay ingestion process, but it could be if
    you want to only go through macro actions in their exact frames.
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

    # Extracting map information
    height_map_minimap = obs.observation.feature_layer_data.minimap_renders.height_map
    starting_location = None
    for unit in obs.observation.raw_data.units:
        unit_doc = get_unit_doc(unit)
        if units_raw[unit_doc["unit_type"]].name in [
            "CommandCenter",
            "Nexus",
            "Hatchery",
        ]:
            if unit.alliance == 1:
                starting_location = unit_doc["location"]
                break

    try:
        assert starting_location != None
    except AssertionError:
        print("Wasn't able to determine a player's starting locations, weird")

    minimap = {"minimap": {"height_map": MessageToDict(height_map_minimap)}}

    actions = {}  # a dict of action dics which is to be merged to actual macro actions.
    states = {}
    scores = {}

    # a list that will hold the frames in which macro actions START to take place. i.e. the left limit of the time interval.
    active_frames = []

    # Initialization of docs.
    initial_frame = obs.observation.game_loop

    new_actions = get_actions(obs.actions, abilities)
    states[str(initial_frame)] = get_state(obs.observation)
    actions[str(initial_frame)] = new_actions
    scores[str(initial_frame)] = get_score(obs.observation)

    # running through the replay
    while True:
        try:
            controller.step(STEP_MULT)
            obs = controller.observe()
            frame_id = obs.observation.game_loop

            new_actions = get_actions(obs.actions, abilities)
            if len(new_actions) == 0:
                # i.e. no op
                states[str(frame_id)] = get_state(obs.observation)
                actions[str(frame_id)] = new_actions
                scores[str(frame_id)] = get_score(obs.observation)
            if len(new_actions) > 0:
                active_frames.append(frame_id - STEP_MULT)

        except ProtocolError:
            obs = controller.observe()
            print(f"last frame recorded: {obs.observation.game_loop}")
            break

    return (states, actions, scores, active_frames, minimap, starting_location)


def extract_macro_actions(
    controller, replay_data, map_data, player_id, macro_action_frames
):
    """
    This function takes macro_action_frames (given by extract_action_frames) and moves through
    the replay only considering the places in which macro actions took place.
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
    actions = {}
    states = {}
    scores = {}
    past_frame = obs.observation.game_loop

    for frame in macro_action_frames:
        if past_frame == 0:
            controller.step(frame - past_frame)
        else:
            controller.step(frame - past_frame - 1)
        obs = controller.observe()
        assert obs.observation.game_loop == frame

        for _ in range(STEP_MULT):
            obs = controller.observe()
            frame_id = obs.observation.game_loop

            new_actions = get_actions(obs.actions, abilities)
            if len(new_actions) > 0:
                # i.e. if they're not no-ops:
                states[str(frame_id)] = get_state(obs.observation)
                actions[str(frame_id)] = new_actions
                scores[str(frame_id)] = get_score(obs.observation)

            controller.step(1)

        past_frame = obs.observation.game_loop

    return states, actions, scores
