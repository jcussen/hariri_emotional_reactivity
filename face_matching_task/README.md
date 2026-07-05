# Emotional Face-Matching Task

Plain Python PsychoPy implementation of a Hariri-style emotional face-matching task with a shape-matching control condition.

## Setup And Run

This project uses the same local-environment pattern as the sibling `emotional_reactivity` repo: dependencies live in `face_matching_task/.conda_env`, and PsychoPy preferences live in `face_matching_task/.home`.

Create or update the environment once:

```bash
bash setup_env.sh
```

Windowed test run:

```bash
bash run_with_env.sh --window
```

Fullscreen run:

```bash
bash run_with_env.sh
```

`window`, `--window`, and `--windowed` all open a window. Without one of those arguments, the task runs fullscreen.

The prompting helper is still available:

```bash
bash run_task.sh window
bash run_task.sh TEST01 01 01 window
```

If the NimStim folder is not at the default macOS path, pass it as the fourth argument:

```bash
bash validate_task.sh /path/to/NimStim_ER
bash run_task.sh TEST01 01 01 /path/to/NimStim_ER window
```

On Windows Git Bash, use forward-slash paths:

```bash
bash setup_env.sh
bash run_task.sh TEST01 01 01 /c/Users/you/path/to/NimStim_ER window
```

You can also set `FACE_STIM_DIR` once instead of passing the path every time:

```bash
export FACE_STIM_DIR=/c/Users/you/path/to/NimStim_ER
bash validate_task.sh
bash run_task.sh TEST01 01 01
```

The manual conda commands are:

```bash
cd face_matching_task
conda env create -p ./.conda_env -f environment.yml
./run_with_env.sh --window
```

If the environment already exists, update it instead:

```bash
cd face_matching_task
conda env update -p ./.conda_env -f environment.yml --prune
```

To run the full task with participant details supplied on the command line:

```bash
cd face_matching_task
./run_with_env.sh --participant-id TEST01 --session 01 --run 01 --window
```

## Validate Stimuli First

Run this before opening a PsychoPy window:

```bash
bash validate_task.sh
```

This checks the requested NimStim identities, writes a stimulus validation report to `data/stimulus_validation_report.json`, and writes a reproducible schedule CSV for a validation participant.

Use a seed when you need the same schedule again:

```bash
bash run_with_env.sh --validate-only --seed 1234
bash run_with_env.sh --seed 1234
```

## Stimulus Path And Identities

The default NimStim path and identity list are in `task/config.py`:

```python
DEFAULT_NIMSTIM_DIR = Path("/Users/joecussen/Documents/Jobs/unimelb/projects/breathwork/resources/faces/NimStim_ER")
NIMSTIM_IDENTITIES = ("01F", "07F", "09F", "13F", "18F", "32M", "34M", "37M", "39M", "40M")
```

You can also override the stimulus directory at runtime:

```bash
bash run_with_env.sh --stim-dir /path/to/NimStim_ER
```

The matcher searches recursively and accepts compact NimStim codes such as `AN` and `FE` as well as word variants such as `angry`, `anger`, `fear`, and `fearful`.

## Output

Behavioural data are saved under:

```text
data/sub-<participant_id>/
```

The task writes:

```text
sub-<id>_task-faceMatching_events.csv
sub-<id>_task-faceMatching_schedule.csv
sub-<id>_task-faceMatching_summary.json
```

Schedule CSV files are written before the PsychoPy task starts. Event and summary files are also written if the participant quits early with `escape`.

## Controls

- `left`: lower-left stimulus matches the target
- `right`: lower-right stimulus matches the target
- `space`: continue instruction screens
- `escape`: quit early
