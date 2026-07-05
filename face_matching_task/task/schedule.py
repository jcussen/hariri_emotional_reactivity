from __future__ import annotations

import csv
import random
from collections import Counter
from pathlib import Path
from typing import Any

from . import config
from .stimuli import StimulusSet


class ScheduleError(RuntimeError):
    pass


def generate_main_schedule(
    stimulus_set: StimulusSet,
    participant_id: str,
    session: str,
    run: str,
    seed: int | None = None,
) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    metadata = {"participant_id": participant_id, "session": session, "run": run}

    face_count = config.BLOCK_ORDER.count("face") * config.TRIALS_PER_BLOCK
    shape_count = config.BLOCK_ORDER.count("shape") * config.TRIALS_PER_BLOCK
    face_specs = _make_face_specs(stimulus_set, face_count, rng, practice=False)
    shape_specs = _make_shape_specs(shape_count, rng, practice=False)
    rng.shuffle(face_specs)
    rng.shuffle(shape_specs)

    rows: list[dict[str, Any]] = []
    face_cursor = 0
    shape_cursor = 0
    global_index = 1

    for block_index, block_type in enumerate(config.BLOCK_ORDER, start=1):
        if block_type == "face":
            block_specs = face_specs[face_cursor : face_cursor + config.TRIALS_PER_BLOCK]
            face_cursor += config.TRIALS_PER_BLOCK
        else:
            block_specs = shape_specs[shape_cursor : shape_cursor + config.TRIALS_PER_BLOCK]
            shape_cursor += config.TRIALS_PER_BLOCK
        rng.shuffle(block_specs)

        for trial_index_in_block, spec in enumerate(block_specs, start=1):
            row = _base_row(
                metadata,
                phase="main",
                block_index=block_index,
                block_type=block_type,
                trial_index_global=global_index,
                trial_index_in_block=trial_index_in_block,
            )
            row.update(spec)
            rows.append(row)
            global_index += 1

    return rows


def generate_practice_schedule(
    stimulus_set: StimulusSet,
    participant_id: str,
    session: str,
    run: str,
    seed: int | None = None,
) -> list[dict[str, Any]]:
    rng = random.Random(None if seed is None else seed + 10_000)
    metadata = {"participant_id": participant_id, "session": session, "run": run}
    typed_specs: list[tuple[str, dict[str, Any]]] = [
        ("face", spec)
        for spec in _make_face_specs(
            stimulus_set,
            config.PRACTICE_FACE_TRIALS,
            rng,
            practice=True,
        )
    ]
    typed_specs.extend(
        ("shape", spec)
        for spec in _make_shape_specs(config.PRACTICE_SHAPE_TRIALS, rng, practice=True)
    )

    rows: list[dict[str, Any]] = []
    for index, (block_type, spec) in enumerate(typed_specs, start=1):
        row = _base_row(
            metadata,
            phase="practice",
            block_index=0,
            block_type=block_type,
            trial_index_global=index,
            trial_index_in_block=index,
        )
        row.update(spec)
        rows.append(row)
    return rows


def save_schedule_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=config.DATA_COLUMNS,
            extrasaction="ignore",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _make_face_specs(
    stimulus_set: StimulusSet,
    total_trials: int,
    rng: random.Random,
    practice: bool,
) -> list[dict[str, Any]]:
    identities_by_sex = stimulus_set.identities_by_sex()
    unusable = {sex: ids for sex, ids in identities_by_sex.items() if len(ids) < 3}
    if unusable:
        details = ", ".join(f"{sex}: {', '.join(ids)}" for sex, ids in unusable.items())
        raise ScheduleError(
            "Strict same-sex face trials require at least 3 identities per displayed sex. "
            f"Insufficient identities: {details}"
        )

    sexes = _balanced_sequence(tuple(sorted(identities_by_sex)), total_trials)
    target_emotions = _balanced_sequence(config.FACE_EMOTIONS, total_trials)
    correct_sides = _balanced_sequence(("left", "right"), total_trials)
    rng.shuffle(sexes)
    rng.shuffle(target_emotions)
    rng.shuffle(correct_sides)

    identity_counts: Counter[str] = Counter()
    target_counts: Counter[str] = Counter()
    specs: list[dict[str, Any]] = []

    for sex, target_emotion, correct_side in zip(sexes, target_emotions, correct_sides):
        same_sex_ids = identities_by_sex[sex]
        target_identity = _choose_least_used(same_sex_ids, rng, target_counts, identity_counts)
        lower_pool = [identity for identity in same_sex_ids if identity != target_identity]
        match_identity = _choose_least_used(lower_pool, rng, identity_counts)
        distractor_pool = [
            identity for identity in lower_pool if identity != match_identity
        ]
        distractor_identity = _choose_least_used(distractor_pool, rng, identity_counts)

        spec = _face_spec(
            stimulus_set,
            target_identity=target_identity,
            match_identity=match_identity,
            distractor_identity=distractor_identity,
            target_emotion=target_emotion,
            correct_side=correct_side,
            iti_duration=config.PRACTICE_ITI if practice else rng.choice(config.FACE_ITI_OPTIONS),
        )
        specs.append(spec)
        identity_counts.update([target_identity, match_identity, distractor_identity])
        target_counts.update([target_identity])

    return specs


def _make_shape_specs(
    total_trials: int,
    rng: random.Random,
    practice: bool,
) -> list[dict[str, Any]]:
    correct_sides = _balanced_sequence(("left", "right"), total_trials)
    rng.shuffle(correct_sides)
    specs: list[dict[str, Any]] = []
    shape_counts: Counter[str] = Counter()

    for correct_side in correct_sides:
        target_shape = _choose_least_used(config.SHAPE_NAMES, rng, shape_counts)
        distractor_choices = [shape for shape in config.SHAPE_NAMES if shape != target_shape]
        distractor_shape = _choose_least_used(distractor_choices, rng, shape_counts)
        specs.append(
            _shape_spec(
                target_shape=target_shape,
                distractor_shape=distractor_shape,
                correct_side=correct_side,
                iti_duration=config.PRACTICE_ITI if practice else config.SHAPE_ITI,
            )
        )
        shape_counts.update([target_shape, distractor_shape])

    return specs


def _face_spec(
    stimulus_set: StimulusSet,
    target_identity: str,
    match_identity: str,
    distractor_identity: str,
    target_emotion: str,
    correct_side: str,
    iti_duration: float,
) -> dict[str, Any]:
    other_emotion = "fearful" if target_emotion == "angry" else "angry"
    if correct_side == "left":
        left_identity = match_identity
        left_emotion = target_emotion
        right_identity = distractor_identity
        right_emotion = other_emotion
    else:
        left_identity = distractor_identity
        left_emotion = other_emotion
        right_identity = match_identity
        right_emotion = target_emotion

    return {
        "target_emotion": target_emotion,
        "left_emotion": left_emotion,
        "right_emotion": right_emotion,
        "target_identity": target_identity,
        "left_identity": left_identity,
        "right_identity": right_identity,
        "target_stim_path": str(stimulus_set.stimuli[target_identity][target_emotion].path),
        "left_stim_path": str(stimulus_set.stimuli[left_identity][left_emotion].path),
        "right_stim_path": str(stimulus_set.stimuli[right_identity][right_emotion].path),
        "correct_side": correct_side,
        "iti_duration": iti_duration,
    }


def _shape_spec(
    target_shape: str,
    distractor_shape: str,
    correct_side: str,
    iti_duration: float,
) -> dict[str, Any]:
    if correct_side == "left":
        left_shape = target_shape
        right_shape = distractor_shape
    else:
        left_shape = distractor_shape
        right_shape = target_shape

    return {
        "target_shape": target_shape,
        "left_shape": left_shape,
        "right_shape": right_shape,
        "target_stim_path": target_shape,
        "left_stim_path": left_shape,
        "right_stim_path": right_shape,
        "correct_side": correct_side,
        "iti_duration": iti_duration,
    }


def _base_row(
    metadata: dict[str, str],
    phase: str,
    block_index: int,
    block_type: str,
    trial_index_global: int,
    trial_index_in_block: int,
) -> dict[str, Any]:
    row = {column: "" for column in config.DATA_COLUMNS}
    row.update(
        {
            "participant_id": metadata["participant_id"],
            "session": metadata["session"],
            "run": metadata["run"],
            "phase": phase,
            "block_index": block_index,
            "block_type": block_type,
            "trial_index_global": trial_index_global,
            "trial_index_in_block": trial_index_in_block,
        }
    )
    return row


def _balanced_sequence(values: tuple[str, ...], total: int) -> list[str]:
    if not values:
        raise ScheduleError("Cannot balance an empty sequence.")
    sequence = [values[index % len(values)] for index in range(total)]
    return sequence


def _choose_least_used(
    candidates: list[str] | tuple[str, ...],
    rng: random.Random,
    primary_counts: Counter[str],
    secondary_counts: Counter[str] | None = None,
) -> str:
    if not candidates:
        raise ScheduleError("No candidates available for trial generation.")
    secondary_counts = secondary_counts or Counter()
    return min(
        candidates,
        key=lambda value: (
            primary_counts[value],
            secondary_counts[value],
            rng.random(),
        ),
    )
