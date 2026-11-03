# Cadence — personal training log

Working browser app: custom workouts, RP history import, editable set logging, feedback, resumable sessions, history and JSON backup/restore. Data stays in IndexedDB on the current device; no login, remote data storage or cross-device sync. Clearing browser storage removes records; download backups regularly. Imported RP records are never modified by new session logging.

## Local run

Python 3.10+ and Node 22+ for tests. No npm dependencies.

```
python -m http.server 8080 --directory web
```

Open http://localhost:8080. Create a session or choose Training blocks → Add starter block. Starter weights are placeholders. Import RP history from Your data; unzip your RP archive and select the JSON file. Backup/restore files use a separate Cadence format.

## Deployment

In GitHub Settings → Pages, select GitHub Actions as the source once. The pages workflow tests and deploys web/ after pushes to main. It can also be run manually from Actions. Pull requests run checks without publishing. No personal export is shipped with the site.

## Verification

```
node --test tests/model.test.mjs
node --check web/app.mjs
python -m unittest discover -s research
```

## Current limits

No automatic weight/volume progression yet. Imported targets are saved RP recommendations, not recalculated prescriptions. Feedback in new logs uses independent descriptive labels, not unverified RP numeric codes. Training block creation/editing, automatic deloads, installable offline mode and sync are future work. Browser UI verification is separate from model tests.

The research/ directory contains the original Python importer and exploratory comparison tool. Its baseline is not the recovered RP algorithm or a ready coaching engine.
