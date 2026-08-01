import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

RUST_SERVER_HOST = os.getenv("RUST_SERVER_HOST", "127.0.0.1")
RUST_SERVER_PORT = int(os.getenv("RUST_SERVER_PORT", "28017"))

RCON_HOST = os.getenv("RCON_HOST", RUST_SERVER_HOST)
RCON_PORT = int(os.getenv("RCON_PORT", "28016"))
RCON_PASSWORD = os.getenv("RCON_PASSWORD")
RCON_TIMEOUT = int(os.getenv("RCON_TIMEOUT", "3"))

UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "30"))

_BOT_DIR = os.path.dirname(os.path.abspath(__file__))

# プロセス検出用（オプション）
WIPE_FLAG_FILE = os.getenv("WIPE_FLAG_FILE")  # ワイプ中を示すファイルパス

# メンテナンスフラグファイル（bot/ と同階層に maintenance.txt を置くと有効）
MAINTENANCE_FLAG_FILE = os.getenv(
    "MAINTENANCE_FLAG_FILE",
    os.path.join(_BOT_DIR, "maintenance.txt"),
)
