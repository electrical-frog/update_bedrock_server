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
- systemd service で Bedrock Server を管理
- 更新されたサーバーだけ更新後に `systemctl restart`
- 既に最新バージョンのサーバーはスキップ
- 複数サーバー構成に対応
- 更新前に `worlds/` 等を `backups/` へバックアップ（最新 N 世代のみ保持）
- 更新後に古いバージョンのディレクトリをクリーンアップ（直近 N 世代は保持）
- systemd timer で定期実行（毎朝など）

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
├── backup.py        # 更新前のバックアップと旧バックアップ削除
├── clean.py         # 古いバージョンディレクトリのクリーンアップ
├── service.py       # systemd restart 処理
├── install_systemd.py # systemd unit のインストール補助
├── systemd/         # systemd unit template
│   ├── bedrock@.service      # サーバー起動用 template unit
│   ├── bedrock-update.service # 更新実行用 oneshot unit
│   └── bedrock-update.timer   # 定期実行用 timer
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

バックアップと定期実行の設定も `config.py` にあります。

```python
backupBeforeUpdate = True
backupDir = 'backups'
backupKeep = 3

updateSchedule = '*-*-* 05:00:00'
```

- `backupBeforeUpdate`: 更新前に `worlds/` 等をバックアップするか
- `backupDir`: バックアップ先ディレクトリ。相対パスの場合は `insDir` 基準です
- `backupKeep`: サーバーごとに保持するバックアップ世代数（古い順に削除）
- `updateSchedule`: 定期実行の `OnCalendar` 指定（systemd timer 用）

クリーンアップの設定:

```python
cleanupAfterUpdate = True
oldKeep = 2
cleanupVerifyService = True
```

- `cleanupAfterUpdate`: 更新後に古いバージョンのディレクトリを削除するか
- `oldKeep`: サーバーごとに保持する旧バージョンのディレクトリ数（直近 N 世代。0=全削除）
- `cleanupVerifyService`: 削除前に `systemctl is-active` でサーバーの稼働を確認するか。非 active のサーバーはスキップされます

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
├── backups/
└── start_server_survival.sh
```

旧バージョンのディレクトリは削除しません。
`backups/` には更新前の `worlds/` 等がサーバーごとに保存されます。

## systemd Setup

このリポジトリは systemd template unit を使ってサーバーを管理します。設定ファイルの実体は1つです。

```text
/etc/systemd/system/bedrock@.service
```

`bedrock@.service` の `@` は template unit を表します。サービス名の `@` の後ろにある文字列が `%i` に入ります。

```text
bedrock@survival.service  -> %i = survival
bedrock@creative.service  -> %i = creative
bedrock@survival2.service -> %i = survival2
```

unit 内では `%i` を使って、サーバーごとの `current_<server>` symlink を起動します。

```ini
WorkingDirectory=/root/bedrock_server/current_%i
ExecStart=/root/bedrock_server/current_%i/bedrock_server
```

そのため `bedrock@survival.service` は、実質的に次を起動します。

```text
/root/bedrock_server/current_survival/bedrock_server
```

サービスはサーバーごとに個別管理できます。

```text
bedrock@survival.service
bedrock@creative.service
bedrock@survival2.service
```

更新時には `current_<server>` symlink が新バージョンのディレクトリへ切り替わります。

systemd unit をインストールし、既存の Bedrock 用 `@reboot` crontab を削除するには次を実行します。

```bash
python3 install_systemd.py
```

インストール後、サービスを起動します。

```bash
systemctl start bedrock@survival.service
systemctl start bedrock@creative.service
systemctl start bedrock@survival2.service
```

状態確認:

```bash
systemctl status bedrock@survival.service
systemctl is-enabled bedrock@survival.service
systemctl cat bedrock@survival.service
```

`is-enabled` が `enabled` なら、ホスト再起動後も自動起動します。

ログ確認:

```bash
journalctl -u bedrock@survival.service -f
journalctl -u bedrock@survival.service -b
```

`-f` は追跡表示、`-b` は現在のブート以降のログ表示です。

個別 restart:

```bash
systemctl restart bedrock@survival.service
```

## 定期実行（systemd timer）

`install_systemd.py` はサーバー用 unit のほかに、更新用 unit もインストールして timer を有効化・開始します。

```text
/etc/systemd/system/bedrock-update.service  # oneshot。python3 main.py を実行
/etc/systemd/system/bedrock-update.timer    # 毎朝 05:00 実行（config の updateSchedule）
```

設定変更（実行時刻など）は `config.py` を編集してから再インストールします。

```bash
python3 install_systemd.py
```

確認:

```bash
systemctl list-timers bedrock-update.timer
systemctl status bedrock-update.service
journalctl -u bedrock-update.service -b
```

- 最新バージョンがなければ各サーバーは `already latest` として即終了します
- `Persistent=true` のため、実行を見逃した場合（停電・再起動中など）は次回起動時に 1 回補います
- 実行ログは journal に記録されます

手動で 1 回だけ実行する場合:

```bash
systemctl start bedrock-update.service
```

## 古いバージョンのクリーンアップ

更新後は自動的に古いバージョンのディレクトリが削除されます。削除には次のガードがあります。

- 削除対象は `current_<name>` シンボリックリンクの指すディレクトリ（稼働中）以外の `bedrock-server-<ver>_<name>` のみ
- 削除直前にシンボリックリンクを再解決して、稼働中ディレクトリでないことを再確認
- `worlds/` 等（`copyTargets`）が稼働中ディレクトリにコピー済みであることを確認
- `cleanupVerifyService = True` の場合、`systemctl is-active` で稼働を確認できないサーバーはスキップ
- `oldKeep` 世代（デフォルト 2）は削除されません

単体実行（`--dry-run` で削除予定の表示のみ）:

```bash
python3 clean.py --dry-run
python3 clean.py
```

## Usage

```bash
python3 main.py
```

サーバーが稼働中であっても実行できます。ワールドデータは稼働中のサーバーからコピーされ、更新されたサーバーは更新後に再起動されます（`restartAfterUpdate = True`）。

実行例:

```text
Downloading: https://www.minecraft.net/bedrockdedicatedserver/bin-linux/bedrock-server-1.26.14.1.zip
Downloaded: /path/to/update_bedrock_server/downloads/bedrock-server-1.26.14.1.zip
survival: 1.21.120.4 -> 1.26.14.1
Done: survival
creative: 1.21.120.4 -> 1.26.14.1
Done: creative
```

既に最新バージョンの場合は、そのサーバーの更新をスキップします。

```text
survival: already latest (1.26.14.1)
```

更新後、必要に応じてサーバーを再起動します。

`config.py` の `restartAfterUpdate = True` の場合、更新されたサーバーだけ `systemctl restart` されます。既に最新でスキップされたサーバーは再起動しません。

## Safety Notes

- サーバー稼働中にコピーされるため、ワールドデータは直近のセーブ時点のスナップショットです。
- 更新前に `worlds/` 等は `backups/<サーバー名>/` へ自動バックアップされます（`backupKeep` 世代分のみ保持）。
- 旧バージョンのディレクトリは `oldKeep` 世代を超えると自動クリーンアップされます。ロールバックが必要な場合は、保持されている旧ディレクトリへ `current_<name>` を戻してから `systemctl restart` してください。
- `start_server_<name>.sh` は新バージョンのディレクトリを向くように書き換えられます。
- `current_<name>` symlink は新バージョンのディレクトリを向くように更新されます。
- 新バージョンの展開先が既に存在する場合、意図しない上書きを避けるため中断します。

## Testing

各モジュールは単体実行で自己テストが走ります。

```bash
python3 paths.py
python3 file_ops.py
python3 versions.py
python3 downloader.py
python3 backup.py
python3 updater.py
python3 service.py
python3 clean.py --test
python3 install_systemd.py --test
python3 main.py --test
```

構文チェック:

```bash
python3 -m py_compile main.py config.py paths.py file_ops.py versions.py downloader.py backup.py updater.py clean.py service.py install_systemd.py
```

最新版 URL 解決だけを確認する場合:

```bash
python3 - <<'PY'
import downloader
print(downloader.resolve_latest_linux_server())
PY
```

## Development

`main.py` はエントリーポイントです。更新手順そのものは `updater.py`、ネットワーク処理は `downloader.py`、バージョン検出は `versions.py`、更新前のバックアップは `backup.py` に分けています。

設定値やハードコードを追加する場合は、まず `config.py` に置けるか確認してください。パス生成は `paths.py` に集約してください。

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
