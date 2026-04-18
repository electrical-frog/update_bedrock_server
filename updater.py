import os

import config
import file_ops
import paths


def update_server_properties(server_name, server_settings, new_version):
    properties_path = paths.server_file(
        new_version,
        server_name,
        config.serverPropertiesName,
    )
    for key, value in server_settings.items():
        file_ops.replace_line_by_prefix(properties_path, f"{key}=", f"{key}={value}")


def copy_existing_data(server_name, old_version, new_version):
    for target in config.copyTargets:
        source = paths.copy_target(old_version, server_name, target)
        destination = paths.copy_target(new_version, server_name, target)
        file_ops.copy_if_exists(source, destination)


def update_binary_permission(server_name, new_version):
    binary_path = paths.server_file(new_version, server_name, config.serverBinaryName)
    os.chmod(binary_path, config.bedrockServerMode)


def update_start_script(server_name, new_version):
    destination_dir = paths.server_dir(new_version, server_name)
    file_ops.replace_line_by_prefix(
        paths.start_script(server_name),
        config.startScriptCdPrefix,
        f"cd {destination_dir}/",
    )


def update_current_link(server_name, version):
    link_path = paths.current_server_link(server_name)
    target_dir = paths.server_dir(version, server_name)
    if not target_dir.exists():
        raise RuntimeError(f"currentリンク先が存在しません: {target_dir}")

    link_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_link = link_path.parent / f".{link_path.name}.tmp"
    if temporary_link.exists() or temporary_link.is_symlink():
        temporary_link.unlink()

    temporary_link.symlink_to(target_dir)
    temporary_link.replace(link_path)


def update_server(server_name, server_settings, old_version, new_version):
    destination_dir = paths.server_dir(new_version, server_name)
    if destination_dir.exists():
        raise RuntimeError(f"更新先ディレクトリが既に存在します: {destination_dir}")

    file_ops.extract_zip(paths.server_zip(new_version), destination_dir)
    update_server_properties(server_name, server_settings, new_version)
    copy_existing_data(server_name, old_version, new_version)
    update_binary_permission(server_name, new_version)
    update_start_script(server_name, new_version)
    update_current_link(server_name, new_version)
    print(f"Done: {server_name}")


def test_update_server():
    from pathlib import Path
    import tempfile
    import zipfile

    original_ins_dir = config.insDir
    original_zip_dir = config.zipDir
    original_copy_targets = config.copyTargets
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config.insDir = str(root / "servers")
            config.zipDir = str(root / "downloads")
            config.copyTargets = ["worlds", "allowlist.json", "permissions.json"]
            Path(config.zipDir).mkdir()
            Path(config.insDir).mkdir()

            old_dir = paths.server_dir("1.0.0", "survival")
            old_dir.mkdir()
            (old_dir / "worlds").mkdir()
            (old_dir / "worlds" / "level.dat").write_text("world", encoding="utf-8")
            (old_dir / "allowlist.json").write_text("[]", encoding="utf-8")
            (old_dir / "permissions.json").write_text("[]", encoding="utf-8")

            paths.start_script("survival").write_text(
                "cd /root/old_server/\n./bedrock_server\n",
                encoding="utf-8",
            )

            with zipfile.ZipFile(paths.server_zip("2.0.0"), "w") as zip_file:
                zip_file.writestr("server.properties", "gamemode=creative\nserver-port=19132\n")
                zip_file.writestr("bedrock_server", "")

            update_server(
                "survival",
                {"gamemode": "survival", "server-port": "19133"},
                "1.0.0",
                "2.0.0",
            )

            new_dir = paths.server_dir("2.0.0", "survival")
            assert (new_dir / "server.properties").read_text(encoding="utf-8") == (
                "gamemode=survival\nserver-port=19133\n"
            )
            assert (new_dir / "worlds" / "level.dat").read_text(encoding="utf-8") == "world"
            assert (new_dir / "allowlist.json").exists()
            assert (new_dir / "permissions.json").exists()
            assert paths.start_script("survival").read_text(encoding="utf-8").startswith(
                f"cd {new_dir}/"
            )
            assert paths.current_server_link("survival").resolve() == new_dir
            try:
                update_server("survival", {}, "1.0.0", "2.0.0")
            except RuntimeError as e:
                assert "更新先ディレクトリが既に存在します" in str(e)
            else:
                raise AssertionError("existing destination should fail")
    finally:
        config.insDir = original_ins_dir
        config.zipDir = original_zip_dir
        config.copyTargets = original_copy_targets


if __name__ == "__main__":
    test_update_server()
    print("updater.py tests passed")
