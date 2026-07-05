from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from task import config
from task.experiment import run_experiment
from task.schedule import (
    generate_main_schedule,
    generate_practice_schedule,
    save_schedule_csv,
)
from task.stimuli import (
    StimulusValidationError,
    format_validation_report,
    validate_stimuli,
)


ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_PARTICIPANT_ID = "TEST01"
DEFAULT_SESSION = "01"
DEFAULT_RUN = "01"


class MetadataCancelled(RuntimeError):
    pass


@dataclass(frozen=True)
class OutputPaths:
    output_dir: Path
    events: Path
    schedule: Path
    summary: Path
    validation_report: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the emotional face-matching task.")
    parser.add_argument("--participant-id", help="Participant ID without the sub- prefix.")
    parser.add_argument("--session", help="Session label. Default in dialog: 01.")
    parser.add_argument("--run", help="Run label. Default in dialog: 01.")
    parser.add_argument("--seed", type=int, help="Optional random seed for reproducible schedules.")
    parser.add_argument(
        "--stim-dir",
        type=Path,
        default=config.DEFAULT_NIMSTIM_DIR,
        help="Path to the NimStim_ER stimulus directory.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate stimuli and generate a schedule without opening a PsychoPy window.",
    )
    parser.add_argument(
        "--window",
        "--windowed",
        dest="windowed",
        action="store_true",
        help="Open the PsychoPy task in a window instead of fullscreen.",
    )
    return parser.parse_args()


def clean_label(value: str) -> str:
    cleaned = "".join(ch for ch in value.strip() if ch.isalnum() or ch in ("-", "_"))
    if not cleaned:
        raise ValueError("Participant/session/run labels cannot be empty.")
    return cleaned


def collect_metadata(args: argparse.Namespace) -> dict[str, str]:
    if args.validate_only:
        return {
            "participant_id": clean_label(args.participant_id or "validate"),
            "session": clean_label(args.session or DEFAULT_SESSION),
            "run": clean_label(args.run or DEFAULT_RUN),
        }

    participant_id = args.participant_id
    session = args.session
    run = args.run

    if not participant_id or not session or not run:
        dialog_metadata = show_metadata_dialog(
            participant_id=participant_id or DEFAULT_PARTICIPANT_ID,
            session=session or DEFAULT_SESSION,
            run=run or DEFAULT_RUN,
        )
        participant_id = dialog_metadata["participant_id"]
        session = dialog_metadata["session"]
        run = dialog_metadata["run"]

    return {
        "participant_id": clean_label(participant_id),
        "session": clean_label(session),
        "run": clean_label(run),
    }


def show_metadata_dialog(participant_id: str, session: str, run: str) -> dict[str, str]:
    from psychopy import gui

    dialog_data = {
        "Participant ID": participant_id,
        "Session": session,
        "Run": run,
    }
    dialog = gui.DlgFromDict(
        dictionary=dialog_data,
        title="Emotional Face-Matching Task",
        order=("Participant ID", "Session", "Run"),
    )
    if not dialog.OK:
        raise MetadataCancelled("Task cancelled before participant details were entered.")

    return {
        "participant_id": dialog_data["Participant ID"],
        "session": dialog_data["Session"],
        "run": dialog_data["Run"],
    }


def build_output_paths(participant_id: str) -> OutputPaths:
    output_dir = config.DATA_DIR / f"sub-{participant_id}"
    prefix = f"sub-{participant_id}_task-faceMatching"
    return OutputPaths(
        output_dir=output_dir,
        events=output_dir / f"{prefix}_events.csv",
        schedule=output_dir / f"{prefix}_schedule.csv",
        summary=output_dir / f"{prefix}_summary.json",
        validation_report=config.DATA_DIR / "stimulus_validation_report.json",
    )


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    args = parse_args()
    try:
        metadata = collect_metadata(args)
    except MetadataCancelled as exc:
        print(exc)
        return 0
    output_paths = build_output_paths(metadata["participant_id"])
    output_paths.output_dir.mkdir(parents=True, exist_ok=True)

    try:
        stimulus_set = validate_stimuli(
            args.stim_dir,
            identities=config.NIMSTIM_IDENTITIES,
            emotions=config.FACE_EMOTIONS,
        )
    except StimulusValidationError as exc:
        write_json(output_paths.validation_report, exc.report)
        print(format_validation_report(exc.report))
        print(f"\nStimulus validation failed:\n{exc}", file=sys.stderr)
        return 1

    write_json(output_paths.validation_report, stimulus_set.report)
    print(format_validation_report(stimulus_set.report))

    main_schedule = generate_main_schedule(
        stimulus_set=stimulus_set,
        participant_id=metadata["participant_id"],
        session=metadata["session"],
        run=metadata["run"],
        seed=args.seed,
    )
    practice_schedule = generate_practice_schedule(
        stimulus_set=stimulus_set,
        participant_id=metadata["participant_id"],
        session=metadata["session"],
        run=metadata["run"],
        seed=args.seed,
    )
    save_schedule_csv(main_schedule, output_paths.schedule)
    print(f"\nSchedule written: {output_paths.schedule}")

    if args.validate_only:
        print(
            f"Validation complete: {len(main_schedule)} main trials and "
            f"{len(practice_schedule)} practice trials generated."
        )
        return 0

    run_experiment(
        main_schedule=main_schedule,
        practice_schedule=practice_schedule,
        output_paths={
            "events": output_paths.events,
            "schedule": output_paths.schedule,
            "summary": output_paths.summary,
        },
        context={
            **metadata,
            "seed": args.seed,
            "stimulus_root": str(stimulus_set.root),
        },
        fullscreen=not args.windowed,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
