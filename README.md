# Rust SrvStatus Bot

Rustサーバーのステータスを取得するDiscord Botです。
現在はステータス取得機能のみ実装されており、自動投稿機能は今後対応予定です。

## ✨ Features

- A2Sによるサーバー情報取得
- Discordに定期投稿 (まだ)
- Docker / systemd 対応
- 軽量・シンプル

---

## Setup

### 1. Clone

```bash
git clone https://github.com/mazurk4/rust-srvstatus-bot.git
cd rust-srvstatus-bot

### 2. 環境変数

```
cp .env.example .env
vim .env
```

## 環境変数

| Name             | Description       |
| ---------------- | ----------------- |
| DISCORD_TOKEN    | Discord Bot Token |
| CHANNEL_ID       | 投稿先チャンネル          |
| RUST_SERVER_HOST | RustサーバーIP(ゲームサーバーと同居する場合はloopバックIPアドレス)        |
| RUST_SERVER_PORT | Queryポート          |
| UPDATE_INTERVAL  | 更新間隔              |

## Docker

```
docker compose up -d --build
```

## systemd

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


sudo cp systemd/rustbot.service.example /etc/systemd/system/rustbot.service
sudo systemctl daemon-reexec
sudo systemctl enable rustbot
sudo systemctl start rustbot
```

## 注意
- RustのQueryポートはUDPです
- server.queryport を使用してください（例: 28017）
- localhostで取得できない場合はグローバルIPを試してください