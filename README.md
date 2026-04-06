# Rust Game SrvStatus Bot

[![Python tests](https://github.com/mazurk4/rust-game-srvstatus-bot/actions/workflows/python-tests.yml/badge.svg)](https://github.com/mazurk4/rust-game-srvstatus-bot/actions/workflows/python-tests.yml)
[![codecov](https://codecov.io/gh/mazurk4/rust-game-srvstatus-bot/branch/main/graph/badge.svg)](https://codecov.io/gh/mazurk4/rust-game-srvstatus-bot)
[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

A Discord bot that retrieves Rust game server status using A2S protocol and displays player count in the bot's status bar.  
Rust サーバーのステータスを取得して Discord Bot のステータス欄にログイン人数を表示する Python 製ボットです。シンプルで軽量、Docker / systemd 対応。

## ✨ Features

- A2S による Rust サーバー情報取得
- Discord ステータス欄にプレイヤー数 / 起動中 / ワイプ中 / Offline を表示
- Docker / systemd 両対応
- シンプルで軽量

## ✨ Features

- A2S による Rust サーバー情報取得
- Discord ステータス欄にプレイヤー数 / 起動中 / ワイプ中 / Offline を表示
- Docker / systemd 両対応
- シンプルで軽量

## 📸 Screenshot

![Discord Bot Status Display](images/status-display.png)

---

## Requirements

- Python 3.12+


## Setup

### 1. Clone

```bash
git clone https://github.com/mazurk4/rust-game-srvstatus-bot.git
cd rust-game-srvstatus-bot
```

### 2. 仮想環境の作成

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 依存関係のインストール

```bash
pip install -e .
```

### 4. 環境変数の設定

```bash
cp .env.example .env
vim .env
```

## 環境変数

| Name             | Description       |
| ---------------- | ----------------- |
| DISCORD_TOKEN    | Discord Bot Token |
| CHANNEL_ID       | 投稿先チャンネル |
| RUST_SERVER_HOST | Rust サーバーの IP / ホスト |
| RUST_SERVER_PORT | Query ポート |
| UPDATE_INTERVAL  | 更新間隔（秒） |
| WIPE_FLAG_FILE   | ワイプ中を示すファイルパス（オプション） |

## Discord セットアップ

詳しい Discord Bot の作成手順は `docs/discord-setup.md` を参照してください。

## Run

```bash
python -m bot.bot
```

## Testing

テストコードは `tests/` フォルダにあります。

```bash
source venv/bin/activate
pip install -e .[dev]
python -m pytest tests -q
```

## Docker

```bash
docker compose up -d --build
```

## systemd

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .

sudo cp systemd/rustbot.service.example /etc/systemd/system/rustbot.service
sudo systemctl daemon-reload
sudo systemctl enable rustbot
sudo systemctl start rustbot
```

- このサンプルは `/opt/rust-srvstatus-bot` 配下に配置する前提です。
- 別のディレクトリに置く場合は、`systemd/rustbot.service.example` の `WorkingDirectory` / `EnvironmentFile` / `ExecStart` を実際のパスに合わせてください。

## Notes

- Rust の Query ポートは UDP です。
- `server.queryport` を使用してください（例: `28017`）。
- `localhost` で取得できない場合はグローバル IP を試してください。
- 実行中のプロセス検出には Linux の `ps` を使います。また、プロセス名に`wipe`文字列を含むをワイプ実行検知としています。
- Discord ステータス表示例:
  - `👥 12/200`
  - `⚙️ Starting`
  - `🔧 Wipe in progress`
  - `🔴 Offline`

## Troubleshooting

- **localhost で取得できない場合**: グローバル IP を試してください。ファイアウォールやネットワーク設定を確認してください。
- **プロセス検出の注意**: ワイプ検出は ps コマンドに依存しており、Linux 専用で環境依存です。ベストエフォートで動作します。必要に応じて特定ファイルの存在確認などに変更してください。
- **ワイプファイル条件**: `WIPE_FLAG_FILE` 環境変数が設定されている場合、そのファイルが存在するとワイプ中と判定します。プロセス名に "wipe" が含まれる場合もワイプ中と判定します。
- **A2S クエリエラー**: タイムアウトやネットワーク断が発生した場合、自動リトライが実装されています。ログを確認してください。

## Roadmap

今後の対応予定機能は [ROADMAP.md](ROADMAP.md) を参照してください.
