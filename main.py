import sys
import urllib.error

import config
import downloader
import service
import updater
import versions


def update_servers():
    try:
        new_version = downloader.prepare_server_zip()
    except urllib.error.URLError as e:
        raise SystemExit(f"ダウンロードサービスへ接続できませんでした: {e}") from e

    updated_servers = []
    for server_name, server_settings in config.settings.items():
        current_version = versions.resolve_current_version(server_name)
        if current_version == new_version:
            updater.update_current_link(server_name, current_version)
            print(f"{server_name}: already latest ({new_version})")
            continue

        old_version = versions.resolve_old_version(server_name, new_version)
        print(f"{server_name}: {old_version} -> {new_version}")
        updater.update_server(server_name, server_settings, old_version, new_version)
        updated_servers.append(server_name)

    service.restart_servers(updated_servers)


def test_update_servers_uses_orchestration():
    calls = []

    original_settings = config.settings
    original_prepare_server_zip = downloader.prepare_server_zip
    original_resolve_current_version = versions.resolve_current_version
    original_resolve_old_version = versions.resolve_old_version
    original_update_server = updater.update_server
    original_restart_servers = service.restart_servers
    try:
        config.settings = {"survival": {"gamemode": "survival"}}
        downloader.prepare_server_zip = lambda: "2.0.0"
        versions.resolve_current_version = lambda server_name: "1.0.0"
        versions.resolve_old_version = lambda server_name, new_version: "1.0.0"

        def fake_update_server(server_name, server_settings, old_version, new_version):
            calls.append((server_name, server_settings, old_version, new_version))

        updater.update_server = fake_update_server
        service.restart_servers = lambda server_names: calls.append(("restart", server_names))
        update_servers()

        assert calls == [
            ("survival", {"gamemode": "survival"}, "1.0.0", "2.0.0"),
            ("restart", ["survival"]),
        ]
    finally:
        config.settings = original_settings
        downloader.prepare_server_zip = original_prepare_server_zip
        versions.resolve_current_version = original_resolve_current_version
        versions.resolve_old_version = original_resolve_old_version
        updater.update_server = original_update_server
        service.restart_servers = original_restart_servers


def test_update_servers_skips_latest():
    calls = []

    original_settings = config.settings
    original_prepare_server_zip = downloader.prepare_server_zip
    original_resolve_current_version = versions.resolve_current_version
    original_resolve_old_version = versions.resolve_old_version
    original_update_server = updater.update_server
    original_update_current_link = updater.update_current_link
    original_restart_servers = service.restart_servers
    try:
        config.settings = {"survival": {"gamemode": "survival"}}
        downloader.prepare_server_zip = lambda: "2.0.0"
        versions.resolve_current_version = lambda server_name: "2.0.0"
        versions.resolve_old_version = lambda server_name, new_version: "should-not-run"
        updater.update_current_link = lambda server_name, version: None

        def fake_update_server(server_name, server_settings, old_version, new_version):
            calls.append((server_name, server_settings, old_version, new_version))

        updater.update_server = fake_update_server
        service.restart_servers = lambda server_names: calls.append(("restart", server_names))
        update_servers()

        assert calls == [("restart", [])]
    finally:
        config.settings = original_settings
        downloader.prepare_server_zip = original_prepare_server_zip
        versions.resolve_current_version = original_resolve_current_version
        versions.resolve_old_version = original_resolve_old_version
        updater.update_server = original_update_server
        updater.update_current_link = original_update_current_link
        service.restart_servers = original_restart_servers


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_update_servers_uses_orchestration()
        test_update_servers_skips_latest()
        print("main.py orchestration test passed")
    else:
        update_servers()
