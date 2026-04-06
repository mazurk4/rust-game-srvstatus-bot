import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

RUST_SERVER_HOST = os.getenv("RUST_SERVER_HOST", "127.0.0.1")
RUST_SERVER_PORT = int(os.getenv("RUST_SERVER_PORT", "28017"))

UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "30"))

# プロセス検出用（オプション）
WIPE_FLAG_FILE = os.getenv("WIPE_FLAG_FILE")  # ワイプ中を示すファイルパス