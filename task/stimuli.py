from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SUPPORTED_IMAGE_EXTENSIONS = {".bmp", ".jpg", ".jpeg", ".png", ".tif", ".tiff"}
EMOTION_ALIASES = {
    "angry": {"an", "ang", "anger", "angry"},
    "fearful": {"fe", "fear", "fearful", "afraid"},
    "happy": {"ha", "hap", "happy"},
    "sad": {"sa", "sad"},
    "neutral": {"ne", "neu", "neutral"},
}


@dataclass(frozen=True)
class StimulusFile:
    identity: str
    emotion: str
    path: Path


@dataclass(frozen=True)
class StimulusSet:
    root: Path
    stimuli: dict[str, dict[str, StimulusFile]]
    report: dict

    def identities_by_sex(self) -> dict[str, list[str]]:
        by_sex: dict[str, list[str]] = {}
        for identity in self.stimuli:
            sex = identity[-1].upper()
            by_sex.setdefault(sex, []).append(identity)
        return {sex: sorted(ids) for sex, ids in by_sex.items()}


class StimulusValidationError(RuntimeError):
    def __init__(self, message: str, report: dict):
        super().__init__(message)
        self.report = report


def validate_stimuli(
    root: Path | str,
    identities: Iterable[str],
    emotions: Iterable[str],
) -> StimulusSet:
    root = Path(root).expanduser().resolve()
    identities = tuple(identity.upper() for identity in identities)
    emotions = tuple(emotions)
    report, chosen = discover_stimuli(root, identities, emotions)

    if report["missing"]:
        missing_text = "\n".join(
            f"  - {item['identity']} {item['emotion']}" for item in report["missing"]
        )
        raise StimulusValidationError(
            f"Missing required NimStim files:\n{missing_text}",
            report,
        )

    return StimulusSet(root=root, stimuli=chosen, report=report)


def discover_stimuli(
    root: Path,
    identities: tuple[str, ...],
    emotions: tuple[str, ...],
) -> tuple[dict, dict[str, dict[str, StimulusFile]]]:
    if not root.exists():
        report = _empty_report(root, identities, emotions)
        report["missing"] = [
            {"identity": identity, "emotion": emotion}
            for identity in identities
            for emotion in emotions
        ]
        report["error"] = f"Stimulus directory does not exist: {root}"
        return report, {}

    candidates: dict[str, dict[str, list[Path]]] = {
        identity: {emotion: [] for emotion in emotions} for identity in identities
    }

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
            continue
        identity = identity_from_name(path.name, identities)
        if identity is None:
            continue
        emotion = emotion_from_name(path.stem, emotions)
        if emotion is None:
            continue
        candidates[identity][emotion].append(path)

    chosen: dict[str, dict[str, StimulusFile]] = {
        identity: {} for identity in identities
    }
    report = _empty_report(root, identities, emotions)

    for identity in identities:
        for emotion in emotions:
            sorted_candidates = sorted(candidates[identity][emotion], key=candidate_sort_key)
            entry = {
                "candidate_count": len(sorted_candidates),
                "chosen": str(sorted_candidates[0]) if sorted_candidates else "",
                "candidates": [str(path) for path in sorted_candidates[:5]],
            }
            report["available"][identity][emotion] = entry
            if sorted_candidates:
                chosen[identity][emotion] = StimulusFile(
                    identity=identity,
                    emotion=emotion,
                    path=sorted_candidates[0],
                )
            else:
                report["missing"].append({"identity": identity, "emotion": emotion})

    return report, chosen


def identity_from_name(filename: str, identities: tuple[str, ...]) -> str | None:
    stem = Path(filename).stem.upper()
    tokens = set(re.split(r"[^A-Z0-9]+", stem))
    for identity in identities:
        identity_upper = identity.upper()
        if identity_upper in tokens or stem.startswith(identity_upper):
            return identity_upper
    return None


def emotion_from_name(stem: str, emotions: tuple[str, ...]) -> str | None:
    lower_stem = stem.lower()
    tokens = set(re.split(r"[^a-z0-9]+", lower_stem))
    for emotion in emotions:
        aliases = EMOTION_ALIASES.get(emotion, {emotion})
        for alias in aliases:
            if alias in tokens:
                return emotion
            if len(alias) > 2 and alias in lower_stem:
                return emotion
    return None


def candidate_sort_key(path: Path) -> tuple[int, int, int, int, str]:
    stem = path.stem.upper()
    is_mirror = 1 if "MIRROR" in stem else 0
    mouth_rank = 2
    if re.search(r"(^|_)C($|_)", stem):
        mouth_rank = 0
    elif re.search(r"(^|_)O($|_)", stem):
        mouth_rank = 1
    extension_rank = {
        ".bmp": 0,
        ".png": 1,
        ".jpg": 2,
        ".jpeg": 2,
        ".tif": 3,
        ".tiff": 3,
    }.get(path.suffix.lower(), 9)
    return (is_mirror, mouth_rank, extension_rank, len(path.name), path.name.lower())


def format_validation_report(report: dict) -> str:
    lines = [
        f"Stimulus root: {report['root']}",
        f"Requested identities: {', '.join(report['identities'])}",
        f"Requested emotions: {', '.join(report['emotions'])}",
        "",
        "Selected stimuli:",
    ]
    for identity in report["identities"]:
        emotion_parts = []
        for emotion in report["emotions"]:
            entry = report["available"][identity][emotion]
            if entry["chosen"]:
                chosen_name = Path(entry["chosen"]).name
                emotion_parts.append(f"{emotion}: {chosen_name}")
            else:
                emotion_parts.append(f"{emotion}: MISSING")
        lines.append(f"  {identity}: " + "; ".join(emotion_parts))

    if report["missing"]:
        lines.append("")
        lines.append("Missing required stimuli:")
        for item in report["missing"]:
            lines.append(f"  - {item['identity']} {item['emotion']}")
    else:
        lines.append("")
        lines.append("Stimulus validation passed.")
    return "\n".join(lines)


def _empty_report(root: Path, identities: tuple[str, ...], emotions: tuple[str, ...]) -> dict:
    return {
        "root": str(root),
        "identities": list(identities),
        "emotions": list(emotions),
        "available": {
            identity: {
                emotion: {"candidate_count": 0, "chosen": "", "candidates": []}
                for emotion in emotions
            }
            for identity in identities
        },
        "missing": [],
    }
