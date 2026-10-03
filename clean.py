import re
import shutil
import subprocess
import sys

import config
import paths
import service
import versions


def running_server_dir(server_name):
    link = paths.current_server_link(server_name)
    if not link.is_symlink():
        raise RuntimeError(f"currentリンクが存在しません: {link}")
    target = link.resolve()
    if not target.is_dir():
        raise RuntimeError(f"currentリンク先が存在しません: {target}")
    pattern = re.compile(rf"bedrock-server-([0-9.]+)_{re.escape(server_name)}$")
    if not pattern.match(target.name):
        raise RuntimeError(f"currentリンク先の形式が不正です: {target}")
    return target


def old_version_dirs(server_name, running_dir):
    candidates = []
    for version in versions.find_existing_versions(server_name):
        directory = paths.server_dir(version, server_name)
        if directory.resolve() == running_dir:
            continue
        candidates.append((directory, version))
    candidates.sort(key=lambda item: versions.version_key(item[1]), reverse=True)
    return candidates


def data_copied_to_running(running_dir, old_dir):
    for target in config.copyTargets:
        if (old_dir / target).exists() and not (running_dir / target).exists():
            return False
    return True


def is_server_active(server_name):
    command = [config.systemctlPath, "is-active", service.service_name(server_name)]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    return result.returncode == 0


def cleanup_server(server_name, dry_run=False):
    running_dir = running_server_dir(server_name)
    to_delete = old_version_dirs(server_name, running_dir)[config.oldKeep:]
    if not to_delete:
        print(f"{server_name}: nothing to clean")
        return []

    if config.cleanupVerifyService and not is_server_active(server_name):
        print(f"{server_name}: service is not active, cleanup skipped")
        return []

    deleted = []
    for directory, version in to_delete:
        current_link = paths.current_server_link(server_name)
        if current_link.is_symlink() and current_link.resolve() == directory.resolve():
            print(f"{server_name}: ABORT - {version} is the running directory")
            break
        if not data_copied_to_running(running_dir, directory):
            print(f"{server_name}: skipped {version} - data not copied to running dir")
            continue
        if dry_run:
            print(f"{server_name}: would delete {directory}")
            continue
        shutil.rmtree(directory)
        deleted.append(directory)
        print(f"{server_name}: deleted {directory}")
    return deleted


def build_scenario(running_version, old_versions):
    for version in old_versions + [running_version]:
        server_dir = paths.server_dir(version, "survival")
        (server_dir / "worlds").mkdir(parents=True, exist_ok=True)
        (server_dir / "worlds" / "level.dat").write_text(f"world-{version}", encoding="utf-8")
        (server_dir / "allowlist.json").write_text("[]", encoding="utf-8")
    link = paths.current_server_link("survival")
    if link.is_symlink() or link.exists():
        link.unlink()
    link.symlink_to(paths.server_dir(running_version, "survival"))


def test_cleanup_server():
    from pathlib import Path
    import tempfile

    original_ins_dir = config.insDir
    original_old_keep = config.oldKeep
    original_verify_service = config.cleanupVerifyService
    original_copy_targets = config.copyTargets
    original_is_active = globals()["is_server_active"]
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config.insDir = str(root)
            config.oldKeep = 1
            config.cleanupVerifyService = True
            config.copyTargets = ["worlds", "allowlist.json"]
            globals()["is_server_active"] = lambda server_name: True

            # 直近 1 世代（1.1.0）だけ残し、1.0.0 を削除する
            build_scenario("1.2.0", ["1.0.0", "1.1.0"])
            deleted = cleanup_server("survival")
            assert [d.name for d in deleted] == ["bedrock-server-1.0.0_survival"]
            assert paths.server_dir("1.1.0", "survival").exists()
            assert paths.server_dir("1.2.0", "survival").exists()

            # サービスが active でなければ削除しない
            build_scenario("1.2.0", ["1.0.0"])
            globals()["is_server_active"] = lambda server_name: False
            deleted = cleanup_server("survival")
            assert deleted == []
            assert paths.server_dir("1.0.0", "survival").exists()
            globals()["is_server_active"] = lambda server_name: True

            # dry-run では削除しない
            config.oldKeep = 0
            deleted = cleanup_server("survival", dry_run=True)
            assert deleted == []
            assert paths.server_dir("1.0.0", "survival").exists()

            # 稼働ディレクトリに未コピーのデータがあれば対象をスキップする
            (paths.server_dir("1.0.0", "survival") / "permissions.json").write_text("[]", encoding="utf-8")
            deleted = cleanup_server("survival", dry_run=True)
            assert deleted == []
            assert paths.server_dir("1.0.0", "survival").exists()
    finally:
        config.insDir = original_ins_dir
        config.oldKeep = original_old_keep
        config.cleanupVerifyService = original_verify_service
        config.copyTargets = original_copy_targets
        globals()["is_server_active"] = original_is_active


def test_cleanup_server_missing_link():
    from pathlib import Path
    import tempfile

    original_ins_dir = config.insDir
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            config.insDir = temp_dir
            paths.server_dir("1.0.0", "survival").mkdir(parents=True)
            try:
                cleanup_server("survival")
            except RuntimeError as e:
                assert "currentリンクが存在しません" in str(e)
            else:
                raise AssertionError("missing current link should fail")
    finally:
        config.insDir = original_ins_dir


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_cleanup_server()
        test_cleanup_server_missing_link()
        print("clean.py tests passed")
    else:
        dry_run = "--dry-run" in sys.argv[1:]
        for server_name in config.settings:
            cleanup_server(server_name, dry_run=dry_run)
