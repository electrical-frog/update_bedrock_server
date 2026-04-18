import shutil
import zipfile


def replace_line_by_prefix(path, target_prefix, replacement_line):
    path = str(path)
    edited_lines = []
    with open(path, "r") as file:
        for line in file:
            if line.startswith(target_prefix):
                edited_lines.append(replacement_line + "\n")
            else:
                edited_lines.append(line)

    with open(path, "w") as file:
        file.writelines(edited_lines)


def extract_zip(zip_path, destination):
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        zip_file.extractall(destination)


def copy_path(source, destination):
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        shutil.copy2(source, destination)


def copy_if_exists(source, destination):
    try:
        copy_path(source, destination)
        return True
    except Exception as e:
        print(f"エラー: {e}")
        return False


def test_replace_line_by_prefix():
    from pathlib import Path
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "server.properties"
        path.write_text("gamemode=creative\nserver-port=19132\n", encoding="utf-8")

        replace_line_by_prefix(path, "gamemode=", "gamemode=survival")

        assert path.read_text(encoding="utf-8") == "gamemode=survival\nserver-port=19132\n"


def test_extract_and_copy():
    from pathlib import Path
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        zip_path = root / "test.zip"
        extracted = root / "extracted"
        copied_file = root / "copied.txt"

        with zipfile.ZipFile(zip_path, "w") as zip_file:
            zip_file.writestr("server.properties", "gamemode=survival\n")

        extract_zip(zip_path, extracted)
        assert (extracted / "server.properties").exists()

        assert copy_if_exists(extracted / "server.properties", copied_file) is True
        assert copied_file.read_text(encoding="utf-8") == "gamemode=survival\n"


if __name__ == "__main__":
    test_replace_line_by_prefix()
    test_extract_and_copy()
    print("file_ops.py tests passed")
