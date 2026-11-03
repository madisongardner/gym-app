# Gym app

Personal workout app under development. Current milestone: Python import and progression research foundation, not a deployed workout app.

## Run the foundation

Requires Python 3.10+; no external dependencies.

```sh
python research/training.py /path/to/rp-training-data.zip --db training.sqlite --out analysis.json
python -m unittest discover -s research
```

Your export stays local. Never commit training databases, exports, credentials or personal workout records. Original exports are preserved in the local SQLite imports table; repeat imports update blocks by ID.

## Next milestones

- Verify feedback-code labels and evaluate muscle-group set progression.
- Build the phone-friendly interface and workout logging.
- Configure a hosting service and automatic deployment once the web app exists.

The experimental constant-percentage model is a research baseline, not RP's recovered algorithm or a ready-to-use coaching engine.
