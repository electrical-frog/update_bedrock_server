import subprocess

import config


def service_name(server_name):
    return f"{config.systemdServicePrefix}{server_name}{config.systemdServiceSuffix}"


def systemctl(*args):
    command = [config.systemctlPath, *args]
    print(" ".join(command))
    subprocess.run(command, check=True)


def restart_servers(server_names):
    if not config.restartAfterUpdate:
        return

    for server_name in server_names:
        systemctl("restart", service_name(server_name))


def test_service_name():
    assert service_name("survival") == "bedrock@survival.service"


def test_restart_servers():
    calls = []

    original_restart_after_update = config.restartAfterUpdate
    original_systemctl = globals()["systemctl"]
    try:
        config.restartAfterUpdate = True

        def fake_systemctl(*args):
            calls.append(args)

        globals()["systemctl"] = fake_systemctl
        restart_servers(["survival", "creative"])

        assert calls == [
            ("restart", "bedrock@survival.service"),
            ("restart", "bedrock@creative.service"),
        ]
    finally:
        config.restartAfterUpdate = original_restart_after_update
        globals()["systemctl"] = original_systemctl


if __name__ == "__main__":
    test_service_name()
    test_restart_servers()
    print("service.py tests passed")
