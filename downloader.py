import json
import re
import shutil
import tempfile
import urllib.request
from pathlib import Path

import config
import paths


LINUX_SERVER_ZIP_RE = re.compile(
    r"https://www\.minecraft\.net/bedrockdedicatedserver/bin-linux/"
    r"bedrock-server-([0-9.]+)\.zip"
)


def fetch_download_links():
    request = urllib.request.Request(
        config.downloadLinksApiUrl,
        headers={
            "Accept": "application/json",
            "User-Agent": config.downloadUserAgent,
        },
    )
    with urllib.request.urlopen(request, timeout=config.apiTimeoutSec) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def resolve_linux_download_from_links(payload):
    links = payload.get("result", {}).get("links", [])
    linux_link = next(
        (
            link.get("downloadUrl")
            for link in links
            if link.get("downloadType") == config.downloadType
        ),
        None,
    )
    if not linux_link:
        raise RuntimeError("Linux版BedrockサーバーのダウンロードURLを取得できませんでした。")

    match = LINUX_SERVER_ZIP_RE.fullmatch(linux_link)
    if not match:
        raise RuntimeError(f"想定外のダウンロードURLです: {linux_link}")

    return match.group(1), linux_link


def resolve_latest_linux_server():
    return resolve_linux_download_from_links(fetch_download_links())


def download_zip(download_url, zip_path):
    zip_path = Path(zip_path)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if zip_path.exists():
        print(f"Download skipped: {zip_path}")
        return False

    print(f"Downloading: {download_url}")
    request = urllib.request.Request(
        download_url,
        headers={"User-Agent": config.downloadUserAgent},
    )
    with urllib.request.urlopen(request, timeout=config.downloadTimeoutSec) as response:
        with tempfile.NamedTemporaryFile(delete=False, dir=zip_path.parent) as temp_file:
            shutil.copyfileobj(response, temp_file)
            temp_path = Path(temp_file.name)

    temp_path.replace(zip_path)
    print(f"Downloaded: {zip_path}")
    return True


def prepare_server_zip():
    if str(config.newVer).lower() == "latest":
        latest_version, download_url = resolve_latest_linux_server()
        download_zip(download_url, paths.server_zip(latest_version))
        return latest_version

    return config.newVer


def test_resolve_linux_download_from_links():
    payload = {
        "result": {
            "links": [
                {
                    "downloadType": "serverBedrockWindows",
                    "downloadUrl": "https://www.minecraft.net/bedrockdedicatedserver/bin-win/bedrock-server-1.2.3.4.zip",
                },
                {
                    "downloadType": "serverBedrockLinux",
                    "downloadUrl": "https://www.minecraft.net/bedrockdedicatedserver/bin-linux/bedrock-server-1.2.3.4.zip",
                },
            ]
        }
    }
    assert resolve_linux_download_from_links(payload) == (
        "1.2.3.4",
        "https://www.minecraft.net/bedrockdedicatedserver/bin-linux/bedrock-server-1.2.3.4.zip",
    )


def test_download_zip_skips_existing_file():
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = Path(temp_dir) / "bedrock-server-1.2.3.4.zip"
        zip_path.write_bytes(b"already here")

        assert download_zip("https://example.com/server.zip", zip_path) is False
        assert zip_path.read_bytes() == b"already here"


if __name__ == "__main__":
    test_resolve_linux_download_from_links()
    test_download_zip_skips_existing_file()
    print("downloader.py tests passed")
