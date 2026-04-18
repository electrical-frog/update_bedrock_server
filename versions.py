import re

import config
import paths


def version_key(version):
    return tuple(int(part) for part in version.split("."))


def find_existing_versions(server_name):
    server_dir_re = re.compile(
        rf"bedrock-server-([0-9.]+)_{re.escape(server_name)}$"
    )
    versions = []
    for path in paths.configured_path(config.insDir).glob(f"bedrock-server-*_{server_name}"):
        if not path.is_dir():
            continue

        match = server_dir_re.match(path.name)
        if match:
            versions.append(match.group(1))

    return sorted(set(versions), key=version_key)


def resolve_current_version(server_name):
    existing_versions = find_existing_versions(server_name)
    if not existing_versions:
        raise RuntimeError(f"{server_name} の既存サーバーが見つかりませんでした。")

    return existing_versions[-1]


def resolve_old_version(server_name, new_version):
    if str(config.oldVer).lower() != "auto":
        return config.oldVer

    candidates = [
        version
        for version in find_existing_versions(server_name)
        if version != new_version
    ]

    if not candidates:
        raise RuntimeError(f"{server_name} のコピー元サーバーが見つかりませんでした。")

    return sorted(set(candidates), key=version_key)[-1]


def test_version_key():
    versions = ["1.21.9.1", "1.21.120.4", "1.21.80.3"]
    assert sorted(versions, key=version_key) == ["1.21.9.1", "1.21.80.3", "1.21.120.4"]


def test_resolve_old_version():
    import tempfile

    original_old_ver = config.oldVer
    original_ins_dir = config.insDir
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            config.oldVer = "auto"
            config.insDir = temp_dir
            for version in ["1.21.80.3", "1.21.114.1", "1.21.120.4"]:
                (paths.configured_path(config.insDir) / f"bedrock-server-{version}_survival").mkdir()

            assert find_existing_versions("survival") == [
                "1.21.80.3",
                "1.21.114.1",
                "1.21.120.4",
            ]
            assert resolve_current_version("survival") == "1.21.120.4"
            assert resolve_old_version("survival", "1.21.120.4") == "1.21.114.1"
            assert resolve_old_version("survival", "1.21.130.1") == "1.21.120.4"
    finally:
        config.oldVer = original_old_ver
        config.insDir = original_ins_dir


if __name__ == "__main__":
    test_version_key()
    test_resolve_old_version()
    print("versions.py tests passed")
