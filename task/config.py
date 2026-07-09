from __future__ import annotations

from pathlib import Path


TASK_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = TASK_ROOT / "data"
DEFAULT_SESSION = "01"
DEFAULT_SCHEDULE_SEED = 1234

# Local, gitignored NimStim_ER folder. Do not commit or publicly share these files.
DEFAULT_NIMSTIM_DIR = TASK_ROOT / "resources" / "NimStim_ER"
NIMSTIM_IDENTITIES = (
    "01F",
    "07F",
    "09F",
    "13F",
    "18F",
    "32M",
    "34M",
    "37M",
    "39M",
    "40M",
)

FACE_EMOTIONS = ("angry", "fearful", "happy", "sad", "neutral")
BLOCK_ORDER = (
    "shape",
    "face",
    "shape",
    "face",
    "shape",
    "face",
    "shape",
    "face",
    "shape",
    "face",
)
TRIALS_PER_BLOCK = 6
PRACTICE_FACE_TRIALS = 5
PRACTICE_SHAPE_TRIALS = 2

LEFT_KEY = "a"
RIGHT_KEY = "b"
QUIT_KEY = "escape"
CONTINUE_KEY = "a"
CONTINUE_BUTTON_LABEL = "button 1"
SCANNER_TRIGGER_KEY = "t"
KEY_TO_SIDE = {LEFT_KEY: "left", RIGHT_KEY: "right"}

TRIAL_RESPONSE_LIMIT = 4.0
PRE_TASK_FIXATION_DURATION = 5.0
POST_TASK_FIXATION_DURATION = 10.0
FACE_ITI_OPTIONS = (2.0, 3.0, 4.0, 5.0, 6.0)
SHAPE_ITI = 2.0
PRACTICE_ITI = 1.0
FEEDBACK_DURATION = 0.75

UNITS = "height"
BACKGROUND_COLOR = "grey"
TEXT_COLOR = "white"
FACE_SIZE = (0.27, 0.36)
TARGET_POS = (0.0, 0.24)
LEFT_POS = (-0.27, -0.18)
RIGHT_POS = (0.27, -0.18)
FIXATION_HEIGHT = 0.07

SHAPES = {
    "circle": {"width": 0.18, "height": 0.18},
    "vertical_ellipse": {"width": 0.13, "height": 0.23},
    "horizontal_ellipse": {"width": 0.24, "height": 0.13},
    "small_circle": {"width": 0.14, "height": 0.14},
}
SHAPE_NAMES = tuple(SHAPES.keys())

DATA_COLUMNS = (
    "participant_id",
    "session",
    "phase",
    "event_type",
    "block_index",
    "block_type",
    "trial_index_global",
    "trial_index_in_block",
    "target_emotion",
    "left_emotion",
    "right_emotion",
    "target_identity",
    "left_identity",
    "right_identity",
    "target_shape",
    "left_shape",
    "right_shape",
    "target_stim_path",
    "left_stim_path",
    "right_stim_path",
    "correct_side",
    "response_key",
    "response_side",
    "correct",
    "rt",
    "trial_start_time",
    "stimulus_onset_time",
    "response_time_abs",
    "event_time_abs",
    "event_duration",
    "iti_duration",
    "missed_response",
)
