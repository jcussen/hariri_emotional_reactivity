from __future__ import annotations

import csv
import json
import math
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any

from . import config


def run_experiment(
    main_schedule: list[dict[str, Any]],
    practice_schedule: list[dict[str, Any]],
    output_paths: dict[str, Path],
    context: dict[str, Any],
    fullscreen: bool = True,
) -> dict[str, Any]:
    from psychopy import core, event, visual

    events: list[dict[str, Any]] = []
    quit_early = False
    started_at = datetime.now().isoformat(timespec="seconds")

    win = visual.Window(
        size=(1100, 800),
        fullscr=fullscreen,
        units=config.UNITS,
        color=config.BACKGROUND_COLOR,
    )
    global_clock = core.Clock()

    try:
        if not _show_text(
            win,
            event,
            "Emotional face matching\n\n"
            "Choose the lower image or shape that matches the target.",
        ):
            quit_early = True

        if not quit_early:
            quit_early = _run_practice(
                win,
                event,
                visual,
                core,
                global_clock,
                practice_schedule,
                events,
                output_paths["events"],
            )

        if not quit_early and not _show_text(
            win,
            event,
            "Main task\n\n"
            "Respond as quickly and accurately as you can.\n"
            "There will be no feedback during the main task.\n\n"
            "Press space to start.",
        ):
            quit_early = True

        if not quit_early:
            quit_early = _run_main_blocks(
                win,
                event,
                visual,
                core,
                global_clock,
                main_schedule,
                events,
                output_paths["events"],
            )

        if not quit_early:
            _show_text(win, event, "Task complete.\n\nPress space to exit.")

    finally:
        summary = _build_summary(
            events=events,
            context=context,
            output_paths=output_paths,
            started_at=started_at,
            quit_early=quit_early,
            main_trials_scheduled=len(main_schedule),
            practice_trials_scheduled=len(practice_schedule),
        )
        _write_events_csv(events, output_paths["events"])
        _write_summary(summary, output_paths["summary"])
        win.close()

    return summary


def _run_practice(
    win: Any,
    event: Any,
    visual: Any,
    core: Any,
    global_clock: Any,
    practice_schedule: list[dict[str, Any]],
    events: list[dict[str, Any]],
    events_path: Path,
) -> bool:
    current_type = ""
    for row in practice_schedule:
        if row["block_type"] != current_type:
            current_type = row["block_type"]
            if not _show_text(
                win,
                event,
                _instruction_text(current_type, practice=True),
            ):
                return True
        event_row, did_quit = _run_trial(
            win,
            event,
            visual,
            core,
            global_clock,
            row,
            feedback=True,
        )
        events.append(event_row)
        _write_events_csv(events, events_path)
        if did_quit:
            return True
    return False


def _run_main_blocks(
    win: Any,
    event: Any,
    visual: Any,
    core: Any,
    global_clock: Any,
    main_schedule: list[dict[str, Any]],
    events: list[dict[str, Any]],
    events_path: Path,
) -> bool:
    rows_by_block: dict[int, list[dict[str, Any]]] = {}
    for row in main_schedule:
        rows_by_block.setdefault(int(row["block_index"]), []).append(row)

    for block_index in sorted(rows_by_block):
        block_rows = rows_by_block[block_index]
        block_type = block_rows[0]["block_type"]
        if not _show_text(win, event, _instruction_text(block_type, practice=False)):
            return True

        for row in block_rows:
            event_row, did_quit = _run_trial(
                win,
                event,
                visual,
                core,
                global_clock,
                row,
                feedback=False,
            )
            events.append(event_row)
            _write_events_csv(events, events_path)
            if did_quit:
                return True
    return False


def _run_trial(
    win: Any,
    event: Any,
    visual: Any,
    core: Any,
    global_clock: Any,
    row: dict[str, Any],
    feedback: bool,
) -> tuple[dict[str, Any], bool]:
    trial_row = dict(row)
    trial_clock = core.Clock()
    trial_row["trial_start_time"] = _format_time(global_clock.getTime())

    event.clearEvents()
    if row["block_type"] == "face":
        _draw_face_trial(win, visual, row)
    else:
        _draw_shape_trial(win, visual, row)

    win.callOnFlip(trial_clock.reset)
    win.flip()
    stimulus_onset = global_clock.getTime()
    trial_row["stimulus_onset_time"] = _format_time(stimulus_onset)

    keys = event.waitKeys(
        maxWait=config.TRIAL_RESPONSE_LIMIT,
        keyList=[config.LEFT_KEY, config.RIGHT_KEY, config.QUIT_KEY],
        timeStamped=trial_clock,
    )

    did_quit = False
    response_key = ""
    response_side = ""
    rt: float | None = None
    response_abs: float | None = None

    if keys:
        response_key, rt = keys[0]
        response_abs = stimulus_onset + float(rt)
        if response_key == config.QUIT_KEY:
            did_quit = True
        else:
            response_side = config.KEY_TO_SIDE.get(response_key, "")

    correct = bool(response_side) and response_side == row["correct_side"]
    missed_response = not bool(response_side)
    trial_row.update(
        {
            "response_key": response_key,
            "response_side": response_side,
            "correct": correct,
            "rt": _format_time(rt) if rt is not None else "",
            "response_time_abs": _format_time(response_abs) if response_abs is not None else "",
            "missed_response": missed_response,
        }
    )

    if feedback and not did_quit:
        if missed_response:
            text = "No response"
        else:
            text = "Correct" if correct else "Incorrect"
        _draw_center_text(win, visual, text)
        win.flip()
        core.wait(config.FEEDBACK_DURATION)

    if not did_quit:
        _draw_fixation(win, visual)
        win.flip()
        core.wait(float(row["iti_duration"]))

    return trial_row, did_quit


def _draw_face_trial(win: Any, visual: Any, row: dict[str, Any]) -> None:
    for key, pos in (
        ("target_stim_path", config.TARGET_POS),
        ("left_stim_path", config.LEFT_POS),
        ("right_stim_path", config.RIGHT_POS),
    ):
        stim = visual.ImageStim(
            win,
            image=row[key],
            pos=pos,
            size=config.FACE_SIZE,
            interpolate=True,
        )
        stim.draw()


def _draw_shape_trial(win: Any, visual: Any, row: dict[str, Any]) -> None:
    for key, pos in (
        ("target_shape", config.TARGET_POS),
        ("left_shape", config.LEFT_POS),
        ("right_shape", config.RIGHT_POS),
    ):
        shape_name = row[key]
        params = config.SHAPES[shape_name]
        stim = visual.ShapeStim(
            win,
            vertices=_ellipse_vertices(params["width"], params["height"]),
            pos=pos,
            fillColor="white",
            lineColor="white",
            lineWidth=2,
            closeShape=True,
        )
        stim.draw()


def _ellipse_vertices(width: float, height: float, points: int = 96) -> list[tuple[float, float]]:
    return [
        (
            math.cos(2 * math.pi * index / points) * width / 2,
            math.sin(2 * math.pi * index / points) * height / 2,
        )
        for index in range(points)
    ]


def _show_text(win: Any, event: Any, text: str) -> bool:
    from psychopy import visual

    _draw_center_text(win, visual, text + "\n\nPress space to continue.")
    win.flip()
    keys = event.waitKeys(keyList=[config.CONTINUE_KEY, config.QUIT_KEY])
    return bool(keys and keys[0] != config.QUIT_KEY)


def _draw_center_text(win: Any, visual: Any, text: str) -> None:
    stim = visual.TextStim(
        win,
        text=text,
        color=config.TEXT_COLOR,
        height=0.035,
        wrapWidth=1.15,
    )
    stim.draw()


def _draw_fixation(win: Any, visual: Any) -> None:
    fixation = visual.TextStim(
        win,
        text="+",
        color=config.TEXT_COLOR,
        height=config.FIXATION_HEIGHT,
    )
    fixation.draw()


def _instruction_text(block_type: str, practice: bool) -> str:
    prefix = "Practice" if practice else "Next block"
    if block_type == "face":
        return (
            f"{prefix}: face matching\n\n"
            "Choose the lower face with the same emotion as the top face."
        )
    return (
        f"{prefix}: shape matching\n\n"
        "Choose the lower shape that matches the top shape."
    )


def _write_events_csv(rows: list[dict[str, Any]], path: Path) -> None:
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


def _write_summary(summary: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def _build_summary(
    events: list[dict[str, Any]],
    context: dict[str, Any],
    output_paths: dict[str, Path],
    started_at: str,
    quit_early: bool,
    main_trials_scheduled: int,
    practice_trials_scheduled: int,
) -> dict[str, Any]:
    main_rows = [row for row in events if row.get("phase") == "main"]
    practice_rows = [row for row in events if row.get("phase") == "practice"]
    answered_main = [row for row in main_rows if row.get("response_side")]
    correct_main = [row for row in main_rows if row.get("correct") is True]
    rt_values = [
        float(row["rt"])
        for row in answered_main
        if row.get("rt") not in ("", None)
    ]

    return {
        **context,
        "started_at": started_at,
        "ended_at": datetime.now().isoformat(timespec="seconds"),
        "quit_early": quit_early,
        "main_trials_scheduled": main_trials_scheduled,
        "main_trials_completed": len(main_rows),
        "practice_trials_scheduled": practice_trials_scheduled,
        "practice_trials_completed": len(practice_rows),
        "main_trials_answered": len(answered_main),
        "main_trials_correct": len(correct_main),
        "main_accuracy": len(correct_main) / len(answered_main) if answered_main else None,
        "main_mean_rt": mean(rt_values) if rt_values else None,
        "events_path": str(output_paths["events"]),
        "schedule_path": str(output_paths["schedule"]),
        "summary_path": str(output_paths["summary"]),
    }


def _format_time(value: float | None) -> str:
    if value is None:
        return ""
    return f"{float(value):.6f}"
