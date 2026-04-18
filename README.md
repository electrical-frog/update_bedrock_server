# update_bedrock_server

Linux 上の Minecraft Bedrock Dedicated Server を、ワールドデータを引き継ぎながら新しいバージョンへ更新する Python スクリプトです。

最新版の解決、Bedrock Server ZIP のダウンロード、既存ワールドと設定ファイルのコピー、起動スクリプトの更新までをまとめて実行できます。

## Features

- Minecraft 公式サービスから Linux 版 Bedrock Server の最新版 URL を取得
- ZIP をリポジトリ内の `downloads/` に自動ダウンロード
- `worlds/`, `allowlist.json`, `permissions.json` を旧バージョンからコピー
- `server.properties` をサーバーごとの設定で更新
- `bedrock_server` に実行権限を付与
- `start_server_<name>.sh` の起動先を新バージョンへ更新
- 複数サーバー構成に対応

## Requirements

- Python 3.10 以降
- Linux
- Minecraft Bedrock Dedicated Server の既存インストール
- 更新対象サーバーの停止

Bedrock Server の Linux 版は Ubuntu 22.04 LTS 以降が公式要件です。詳細は Minecraft 公式ページを確認してください。

https://www.minecraft.net/ja-jp/download/server/bedrock

## Project Structure

```text
.
├── main.py          # エントリーポイント兼オーケストレーション
├── config.py        # バージョン、パス、API、コピー対象などの設定
├── downloader.py    # 最新版URLの解決とZIPダウンロード
├── versions.py      # 既存サーバーのバージョン検出
├── updater.py       # 1サーバー分の更新処理
├── file_ops.py      # ZIP展開、コピー、行置換
├── paths.py         # パス生成
└── downloads/       # ダウンロード済みZIPの保存先
```

`downloads/` 内の ZIP は `.gitignore` で除外されます。

## Installation

```bash
git clone https://github.com/electrical-frog/update_bedrock_server.git
cd update_bedrock_server
```

外部 Python パッケージは不要です。標準ライブラリのみを使います。

## Configuration

[config.py](config.py) を環境に合わせて編集します。

```python
oldVer = 'auto'
newVer = 'latest'

zipDir = './downloads'
insDir = '/root/bedrock_server'
```

- `oldVer = 'auto'`: `insDir` 配下の `bedrock-server-<version>_<server>` から最新の既存バージョンをコピー元にします。
- `newVer = 'latest'`: 公式サービスから最新の Linux 版 ZIP URL を解決してダウンロードします。
- `zipDir`: Bedrock Server ZIP の保存先です。相対パスはこのリポジトリのルート基準です。
- `insDir`: Bedrock Server のインストール先です。

サーバーごとの設定は `settings` に定義します。

```python
settings = {
        'survival': {
            'gamemode': 'survival',
            'difficulty': 'easy',
            'server-port': '19132',
            'server-portv6': '19133',
        },
        'creative': {
            'gamemode': 'creative',
            'difficulty': 'easy',
            'server-port': '19134',
            'server-portv6': '19135',
        },
}
```

キーは Bedrock の `server.properties` と同じ名前にしてください。

## Expected Directory Layout

このツールは、既存サーバーが次の形式で配置されている前提で動きます。

```text
/root/bedrock_server/
├── bedrock-server-1.21.120.4_survival/
├── bedrock-server-1.21.120.4_creative/
├── start_server_survival.sh
└── start_server_creative.sh
```

更新後は次のような新ディレクトリが作られます。

```text
/root/bedrock_server/
├── bedrock-server-1.21.120.4_survival/
├── bedrock-server-1.26.14.1_survival/
└── start_server_survival.sh
```

旧バージョンのディレクトリは削除しません。

## Usage

サーバーを停止してから実行してください。

```bash
python3 main.py
```

実行例:

```text
Downloading: https://www.minecraft.net/bedrockdedicatedserver/bin-linux/bedrock-server-1.26.14.1.zip
Downloaded: /path/to/update_bedrock_server/downloads/bedrock-server-1.26.14.1.zip
survival: 1.21.120.4 -> 1.26.14.1
Done: survival
creative: 1.21.120.4 -> 1.26.14.1
Done: creative
```

更新後、必要に応じてサーバーを再起動します。

```bash
/usr/bin/bash /root/bedrock_server/start_server_survival.sh
```

## Safety Notes

- 実行前に Bedrock Server を停止してください。
- `worlds/` はコピーされますが、念のため事前バックアップを推奨します。
- 旧バージョンのサーバーディレクトリは削除されません。
- `start_server_<name>.sh` は新バージョンのディレクトリを向くように書き換えられます。
- 新バージョンの展開先が既に存在する場合、コピー処理でエラーになることがあります。

## Testing

各モジュールは単体実行で自己テストが走ります。

```bash
python3 paths.py
python3 file_ops.py
python3 versions.py
python3 downloader.py
python3 updater.py
python3 main.py --test
```

構文チェック:

```bash
python3 -m py_compile main.py config.py paths.py file_ops.py versions.py downloader.py updater.py
```

最新版 URL 解決だけを確認する場合:

```bash
python3 - <<'PY'
import downloader
print(downloader.resolve_latest_linux_server())
PY
```

## Development

`main.py` はエントリーポイントです。更新手順そのものは `updater.py`、ネットワーク処理は `downloader.py`、バージョン検出は `versions.py` に分けています。

設定値やハードコードを追加する場合は、まず `config.py` に置けるか確認してください。パス生成は `paths.py` に集約してください。

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
