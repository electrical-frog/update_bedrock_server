from pathlib import Path
import subprocess
import sys

import config
import paths
import updater
import versions


def unit_template_source():
    return config.projectDir / "systemd" / config.systemdUnitTemplate


def unit_template_destination():
    return Path(config.systemdUnitDir) / config.systemdUnitTemplate


def install_unit_template():
    source = unit_template_source()
    destination = unit_template_destination()
    if not source.exists():
        raise RuntimeError(f"systemd unit template が見つかりません: {source}")

    content = source.read_text(encoding="utf-8").format(
        descriptionPrefix=config.systemdDescriptionPrefix,
        insDir=config.insDir.rstrip("/"),
        restartSec=config.systemdRestartSec,
    )
    destination.write_text(content, encoding="utf-8")
    print(f"Installed: {destination}")


def systemctl(*args):
    command = [config.systemctlPath, *args]
    print(" ".join(command))
    subprocess.run(command, check=True)


def remove_cron_reboot_lines():
    current = subprocess.run(
        ["crontab", "-l"],
        check=False,
        capture_output=True,
        text=True,
    )
    if current.returncode != 0 and current.stderr:
        print(current.stderr.strip())
        return

    remove_targets = {
        str(paths.start_script(server_name))
        for server_name in config.settings
    }
    kept_lines = []
    removed_lines = []
    for line in current.stdout.splitlines():
        if line.startswith("@reboot") and any(target in line for target in remove_targets):
            removed_lines.append(line)
        else:
            kept_lines.append(line)

    if not removed_lines:
        print("No Bedrock @reboot crontab entries found.")
        return

    new_crontab = "\n".join(kept_lines).rstrip() + "\n"
    subprocess.run(["crontab", "-"], input=new_crontab, text=True, check=True)
    for line in removed_lines:
        print(f"Removed crontab entry: {line}")


def enable_services():
    for server_name in config.settings:
        current_version = versions.resolve_current_version(server_name)
        updater.update_current_link(server_name, current_version)
        systemctl("enable", f"{config.systemdServicePrefix}{server_name}{config.systemdServiceSuffix}")


def install_systemd_services():
    install_unit_template()
    systemctl("daemon-reload")
    enable_services()
    remove_cron_reboot_lines()
    print("systemd setup complete. Start or restart services with systemctl.")


def test_unit_paths():
    assert unit_template_source() == config.projectDir / "systemd" / "bedrock@.service"
    assert unit_template_destination() == Path("/etc/systemd/system/bedrock@.service")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_unit_paths()
        print("install_systemd.py tests passed")
    else:
        install_systemd_services()
