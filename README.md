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

## Run The Experiment

Windowed test run:

```bash
bash run_task.sh window
```

Fullscreen run:

```bash
bash run_task.sh
```

The task opens a PsychoPy popup for participant ID, session, and run.

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

- 54 main trials total
- 24 emotional face-matching trials: angry and fearful faces
- 30 shape-matching control trials
- 4 practice trials
- 10 actors: `01F, 07F, 09F, 13F, 18F, 32M, 34M, 37M, 39M, 40M`
- Closed-mouth expressions are used first: `AN_C`, `FE_C`
- Response keys: `left = lower-left match`, `right = lower-right match`
- `space` continues instruction screens
- `escape` quits early
