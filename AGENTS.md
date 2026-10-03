# Repository Guidelines

## Project Structure & Module Organization

This repository contains a small Python utility for updating local Minecraft Bedrock server installations.

- `main.py`: update script. It resolves and downloads the new Bedrock server ZIP, backs up world and access-control data, applies `server.properties` settings, copies world and access-control files, updates permissions, and rewrites start scripts.
- `config.py`: local version numbers, ZIP/install directories, per-server settings, and backup/timer options. Treat this as environment-specific configuration.
- `backup.py`: pre-update backup of `worlds/` etc. with generation pruning.
- `clean.py`: guarded cleanup of old version directories (never removes the directory the `current_<name>` symlink points to).
- `systemd/`: unit templates for the servers (`bedrock@.service`) and the scheduled updater (`bedrock-update.service` / `bedrock-update.timer`).
- `README.md`: user-facing setup and operation notes.

There is currently no dedicated `tests/` directory, package metadata, or static asset tree.

## Build, Test, and Development Commands

- `python3 main.py`: run the updater using values from `config.py`.
- `python3 -m py_compile main.py config.py`: quick syntax check without running filesystem updates.
- `git status --short`: check for local configuration edits before committing.

Run the updater only on a host where `zipDir`, `insDir`, old server folders, new ZIP files, and `start_server_<name>.sh` scripts exist. The script performs real file copies and permission changes.

## Coding Style & Naming Conventions

Use Python 3 and keep the script dependency-free unless a change clearly needs a library. Follow PEP 8 for new code: four-space indentation, `snake_case` function and variable names, and clear constants for repeated path patterns. Existing configuration keys mirror Bedrock `server.properties` names, such as `server-port` and `allow-list`; preserve those exact strings.

Prefer `pathlib.Path` for new path-heavy code, but avoid broad rewrites unless they reduce risk. Keep comments short and useful, especially around filesystem operations that can overwrite or copy live server data.

## Testing Guidelines

No automated tests are currently defined. For code changes, at minimum run:

```bash
python3 -m py_compile main.py config.py
```

For behavior changes, test against a disposable Bedrock server directory and ZIP file before using production paths. Verify that `worlds/`, `allowlist.json`, `permissions.json`, `server.properties`, and start scripts are updated as expected.

## Commit & Pull Request Guidelines

Recent commits use short, direct messages, sometimes in Japanese, for example `readme` and `permissions.jsonのコピーに対応`. Keep commits focused and describe the user-visible change.

Pull requests should include the affected workflow, a short test note, and any required `config.py` changes. Do not include private local paths, server credentials, or production-only configuration unless they are intentional examples.

## Security & Configuration Tips

Review `config.py` before running or committing. Local install paths and server names may reveal deployment details. Back up server folders before running updates, especially production `worlds/` data.
