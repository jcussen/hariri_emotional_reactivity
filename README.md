# Emotional Face-Matching Task

PsychoPy experiment for a Hariri-style emotional face-matching task using private `NimStim_ER` face images.

Important: do not commit or publicly upload `NimStim_ER.zip`, `resources/NimStim_ER/`, or data.

## Add The Private Faces

You should have a separate private file:

```text
NimStim_ER.zip
```

Do this before setting up the environment or running the task.

Without using the command line:

1. Double-click `NimStim_ER.zip` to unzip it.
2. You should now have a folder called `NimStim_ER`.
3. Drag that `NimStim_ER` folder into the repo's existing `resources` folder.

The final layout should be:

```text
hariri_emotional_reactivity/
  resources/
    NimStim_ER/
      01F_AN_C.BMP
      01F_FE_C.BMP
      ...
```

## Create The Environment

Run this once from the repo root:

```bash
bash setup_env.sh
```

The setup script installs PsychoPy `2023.2.3`.

## Run The Experiment

Windowed test run:

```bash
bash run_task.sh window
```

Fullscreen run:

```bash
bash run_task.sh
```

Practice-only run:

```bash
bash run_task.sh --practice
```

The task opens a PsychoPy popup with a blank participant-ID field and session number prefilled as `01`.

Results are saved locally in:

```text
data/
```

## Validate Stimuli

Optional check before opening the PsychoPy task:

```bash
bash validate_task.sh
```

## Task Summary

- 60 main trials total
- 30 emotional face-matching trials: angry, fearful, happy, sad, and neutral faces
- 30 shape-matching control trials
- No practice trials are included in the standard run
- `--practice` runs 7 practice trials only
- Trial order is deterministic by default and does not depend on participant ID
- 10 actors: `01F, 07F, 09F, 13F, 18F, 32M, 34M, 37M, 39M, 40M`
- Closed-mouth expressions are used first: `AN_C`, `FE_C`, `HA_C`, `SA_C`, `NE_C`
- Response buttons: `1` = lower-left match, `2` = lower-right match
- Button 1 continues instruction screens
- The standard run waits for scanner trigger `t`, logs the trigger, shows and logs a 5-second fixation cross, then starts
- The standard run ends with an additional 10-second fixation cross after the final face trials
- `escape` quits early
