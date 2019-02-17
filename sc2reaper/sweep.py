from pysc2.lib.protocol import ProtocolError

from sc2reaper.score_extraction import get_score
from sc2reaper.state_extraction import get_state
from sc2reaper.action_extraction import get_actions

STEP_MULTIPLIER = 24

# active_frames = [0, 24, 48]
# saltos = [1, 1, 1...,1, 1, 1, 24, 1, 1, 1...]


def jumps(active_frames=None):
    if active_frames is not None:
        past_frame = -1
        for frame in active_frames:
            big_jump = 0
            while past_frame != frame - 1 and past_frame < frame:
                big_jump += STEP_MULTIPLIER
                past_frame += STEP_MULTIPLIER
            yield big_jump
            for _ in range(STEP_MULTIPLIER):
                yield 1
            past_frame += STEP_MULTIPLIER
    else:
        while True:
            yield STEP_MULTIPLIER


def sweep(controller, abilities, active_frames=None):
    actions = []
    states = []
    scores = []

    for jump in jumps(active_frames):
        try:
            obs = controller.observe()
            frame_id = obs.observation.game_loop

            states.append({"frame_id": frame_id, **get_state(obs.observation)})
            actions.append(
                {"frame_id": frame_id, **get_actions(obs.actions, abilities)}
            )
            scores.append({"frame_id": frame_id, **get_score(obs.observation)})

            controller.step(jump)
        except ProtocolError:
            break

    return actions, states, scores
