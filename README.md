# Rust SrvStatus Bot

[![Python tests](https://github.com/mazurk4/rust-srvstatus-bot/actions/workflows/python-tests.yml/badge.svg)](https://github.com/mazurk4/rust-srvstatus-bot/actions/workflows/python-tests.yml)

Rustサーバーのステータスを取得して BOTのステータス欄にログイン人数を表示する Bot です。
チャンネルへのサーバーダウン通知投稿、ログイン人数投稿機能は今後対応予定です。

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
git clone https://github.com/mazurk4/rust-srvstatus-bot.git
cd rust-srvstatus-bot
```

### 2. 仮想環境の作成

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
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
pip install -r requirements-dev.txt
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
pip install -r requirements.txt

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
