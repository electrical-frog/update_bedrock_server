import sys
import urllib.error

import config
import downloader
import updater
import versions


def update_servers():
    try:
        new_version = downloader.prepare_server_zip()
    except urllib.error.URLError as e:
        raise SystemExit(f"ダウンロードサービスへ接続できませんでした: {e}") from e

    for server_name, server_settings in config.settings.items():
        old_version = versions.resolve_old_version(server_name, new_version)
        print(f"{server_name}: {old_version} -> {new_version}")
        updater.update_server(server_name, server_settings, old_version, new_version)


def test_update_servers_uses_orchestration():
    calls = []

    original_settings = config.settings
    original_prepare_server_zip = downloader.prepare_server_zip
    original_resolve_old_version = versions.resolve_old_version
    original_update_server = updater.update_server
    try:
        config.settings = {"survival": {"gamemode": "survival"}}
        downloader.prepare_server_zip = lambda: "2.0.0"
        versions.resolve_old_version = lambda server_name, new_version: "1.0.0"

        def fake_update_server(server_name, server_settings, old_version, new_version):
            calls.append((server_name, server_settings, old_version, new_version))

        updater.update_server = fake_update_server
        update_servers()

        assert calls == [("survival", {"gamemode": "survival"}, "1.0.0", "2.0.0")]
    finally:
        config.settings = original_settings
        downloader.prepare_server_zip = original_prepare_server_zip
        versions.resolve_old_version = original_resolve_old_version
        updater.update_server = original_update_server


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_update_servers_uses_orchestration()
        print("main.py orchestration test passed")
    else:
        update_servers()
