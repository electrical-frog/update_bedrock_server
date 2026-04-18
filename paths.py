from pathlib import Path

import config


def configured_path(path):
    path = Path(path)
    if path.is_absolute():
        return path

    return config.projectDir / path


def server_dir(version, server_name):
    return configured_path(config.insDir) / f"bedrock-server-{version}_{server_name}"


def server_zip(version):
    return configured_path(config.zipDir) / f"bedrock-server-{version}.zip"


def start_script(server_name):
    return configured_path(config.insDir) / f"{config.startScriptPrefix}{server_name}.sh"


def current_server_link(server_name):
    return configured_path(config.insDir) / f"{config.currentLinkPrefix}{server_name}"


def server_file(version, server_name, filename):
    return server_dir(version, server_name) / filename


def copy_target(version, server_name, target):
    return server_dir(version, server_name) / target


def test_paths():
    original_ins_dir = config.insDir
    original_zip_dir = config.zipDir
    original_project_dir = config.projectDir
    try:
        config.projectDir = Path("/repo")
        config.insDir = "/tmp/bedrock"
        config.zipDir = "downloads"
        assert server_dir("1.2.3", "survival") == Path("/tmp/bedrock/bedrock-server-1.2.3_survival")
        assert server_zip("1.2.3") == Path("/repo/downloads/bedrock-server-1.2.3.zip")
        assert start_script("survival") == Path("/tmp/bedrock/start_server_survival.sh")
        assert current_server_link("survival") == Path("/tmp/bedrock/current_survival")
        assert server_file("1.2.3", "survival", "server.properties") == Path(
            "/tmp/bedrock/bedrock-server-1.2.3_survival/server.properties"
        )
    finally:
        config.insDir = original_ins_dir
        config.zipDir = original_zip_dir
        config.projectDir = original_project_dir


if __name__ == "__main__":
    test_paths()
    print("paths.py tests passed")
