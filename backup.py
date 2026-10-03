import shutil
from datetime import datetime

import config
import file_ops
import paths


def backup_dest(server_name, old_version):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base = f"{timestamp}_{old_version}"
    destination = paths.backup_dir(server_name) / base
    counter = 1
    while destination.exists() or destination.is_symlink():
        counter += 1
        destination = paths.backup_dir(server_name) / f"{base}-{counter}"
    return destination


def backup_server(server_name, old_version):
    if not config.backupBeforeUpdate:
        return
    destination = backup_dest(server_name, old_version)
    destination.mkdir(parents=True, exist_ok=True)
    for target in config.copyTargets:
        source = paths.copy_target(old_version, server_name, target)
        file_ops.copy_if_exists(source, destination / target)
    prune_backups(server_name)
    print(f"Backup: {destination}")


def prune_backups(server_name):
    keep = config.backupKeep
    if keep is None:
        return
    root = paths.backup_dir(server_name)
    if not root.is_dir():
        return
    entries = sorted(
        (path for path in root.iterdir() if path.is_dir()),
        key=lambda path: path.name,
        reverse=True,
    )
    for stale in entries[keep:]:
        shutil.rmtree(stale)
        print(f"Pruned old backup: {stale}")


def test_backup_server():
    from pathlib import Path
    import tempfile

    original_ins_dir = config.insDir
    original_backup_before_update = config.backupBeforeUpdate
    original_backup_keep = config.backupKeep
    original_copy_targets = config.copyTargets
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config.insDir = str(root / "servers")
            config.backupBeforeUpdate = True
            config.backupKeep = 2
            config.copyTargets = ["worlds", "allowlist.json"]

            old_dir = paths.server_dir("1.0.0", "survival")
            (old_dir / "worlds").mkdir(parents=True)
            (old_dir / "worlds" / "level.dat").write_text("world", encoding="utf-8")
            (old_dir / "allowlist.json").write_text("[]", encoding="utf-8")

            import backup

            backup.backup_server("survival", "1.0.0")
            backup.backup_server("survival", "1.0.0")
            backup.backup_server("survival", "1.0.0")

            backup_root = paths.backup_dir("survival")
            entries = sorted(path for path in backup_root.iterdir() if path.is_dir())
            assert len(entries) == 2
            newest = entries[-1]
            assert (newest / "worlds" / "level.dat").read_text(encoding="utf-8") == "world"
            assert (newest / "allowlist.json").exists()

            config.backupBeforeUpdate = False
            backup.backup_server("survival", "1.0.0")
            assert len(list(backup_root.iterdir())) == 2
    finally:
        config.insDir = original_ins_dir
        config.backupBeforeUpdate = original_backup_before_update
        config.backupKeep = original_backup_keep
        config.copyTargets = original_copy_targets


def test_prune_backups_keeps_none():
    from pathlib import Path
    import tempfile

    original_ins_dir = config.insDir
    original_backup_keep = config.backupKeep
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config.insDir = str(root / "servers")
            config.backupKeep = 0

            import backup

            backup_root = paths.backup_dir("survival")
            backup_root.mkdir(parents=True)
            for name in ["20260101-000000_1.0.0", "20260102-000000_1.1.0"]:
                (backup_root / name).mkdir()

            backup.prune_backups("survival")
            assert list(backup_root.iterdir()) == []
    finally:
        config.insDir = original_ins_dir
        config.backupKeep = original_backup_keep


if __name__ == "__main__":
    test_backup_server()
    test_prune_backups_keeps_none()
    print("backup.py tests passed")
