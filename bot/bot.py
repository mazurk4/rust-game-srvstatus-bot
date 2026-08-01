import a2s
import discord
import asyncio
import json
import socket
import subprocess
import logging
import os
from urllib.parse import quote
from .config import *

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
client = discord.Client(intents=intents)


def get_a2s_info(retries=3, delay=1):
    for attempt in range(retries):
        try:
            return a2s.info((RUST_SERVER_HOST, RUST_SERVER_PORT), timeout=3)
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            logger.warning(f"A2S query attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                asyncio.sleep(delay)
        except Exception as e:
            logger.error(f"A2S query error: {e}")
            return None
    logger.error("A2S query failed after all retries")
    return None


def get_process_list():
    try:
        result = subprocess.run(
            ["ps", "-eo", "etimes,args"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"PS command failed: {e}")
        return ""
    except Exception as e:
        logger.error(f"PS error: {e}")
        return ""


def parse_rcon_server_info(message: str):
    try:
        data = json.loads(message)
        return {
            "queue": max(0, int(data["Queued"])),
            "joining": max(0, int(data["Joining"])),
        }
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as e:
        logger.warning(f"Invalid RCON serverinfo response: {e}")
        return None


def get_rcon_server_info(connection_factory=None):
    if not RCON_PASSWORD:
        return None

    if connection_factory is None:
        try:
            from websocket import create_connection
            connection_factory = create_connection
        except ImportError as e:
            logger.warning(f"RCON client is unavailable: {e}")
            return None

    host = f"[{RCON_HOST}]" if ":" in RCON_HOST else RCON_HOST
    password = quote(RCON_PASSWORD, safe="")
    url = f"ws://{host}:{RCON_PORT}/{password}"
    identifier = 1001
    connection = None

    try:
        connection = connection_factory(url, timeout=RCON_TIMEOUT)
        connection.send(json.dumps({
            "Identifier": identifier,
            "Message": "serverinfo",
            "Name": "WebRcon",
        }))

        for _ in range(10):
            response = json.loads(connection.recv())
            if response.get("Identifier") == identifier:
                return parse_rcon_server_info(response.get("Message", ""))

        logger.warning("RCON serverinfo response was not received")
    except Exception as e:
        logger.warning(f"RCON query failed: {e}")
    finally:
        if connection is not None:
            try:
                connection.close()
            except Exception as e:
                logger.warning(f"RCON connection close failed: {e}")

    return None


def parse_process_status(process_output: str):
    # メンテナンスフラグファイルが存在する場合はメンテナンス中
    if MAINTENANCE_FLAG_FILE and os.path.exists(MAINTENANCE_FLAG_FILE):
        return "maintenance"

    # ファイルベースの検出（環境変数定義時のみ）
    if WIPE_FLAG_FILE and os.path.exists(WIPE_FLAG_FILE):
        return "wipe"

    if not process_output:
        return None

    for line in process_output.splitlines():
        line = line.strip()
        if not line:
            continue

        parts = line.split(None, 1)
        if len(parts) != 2:
            continue

        elapsed_str, args = parts
        lower_args = args.lower()
        if "wipe.sh" in lower_args:
            return "wipe"
        if "rustdedicated" not in lower_args:
            continue

        try:
            elapsed = int(elapsed_str)
        except ValueError:
            continue

        if elapsed <= 300:
            return "starting"

    return None


def get_server_info(process_output: str | None = None):
    if process_output is None:
        process_output = get_process_list()

    process_status = parse_process_status(process_output)
    if process_status == "maintenance":
        return {"status": "maintenance"}
    if process_status == "wipe":
        return {"status": "wipe"}
    if process_status == "starting":
        return {"status": "starting"}

    info = get_a2s_info()
    if info is None:
        return None

    server_info = {
        "name": info.server_name,
        "players": info.player_count,
        "max_players": info.max_players,
        "map": info.map_name,
        "ping": round(info.ping * 1000, 2),
    }
    rcon_info = get_rcon_server_info()
    if rcon_info is not None:
        server_info.update(rcon_info)

    return server_info


def format_status_text(server_info):
    if server_info is None:
        return "🔴 Offline"
    if server_info.get("status") == "maintenance":
        return "🛠️ Maintenance"
    if server_info.get("status") == "wipe":
        return "🔧 Wipe in progress"
    if server_info.get("status") == "starting":
        return "⚙️ Starting"

    text = f"👥 {server_info['players']}/{server_info['max_players']}"
    if "queue" in server_info and "joining" in server_info:
        text += f" | Queue {server_info['queue']} | Joining {server_info['joining']}"
    return text


async def update_status():
    await client.wait_until_ready()

    logger.info("Status loop started")

    while not client.is_closed():
        loop = asyncio.get_event_loop()
        status = await loop.run_in_executor(None, get_server_info)
        text = format_status_text(status)

        try:
            await client.change_presence(
                status=discord.Status.online,
                activity=discord.Game(name=text)
            )
            logger.info(f"Status updated: {text}")
        except Exception as e:
            logger.error(f"Discord update error: {e}")

        await asyncio.sleep(UPDATE_INTERVAL)


@client.event
async def on_ready():
    logger.info(f"Logged in as {client.user}")
    client.loop.create_task(update_status())


client.run(DISCORD_TOKEN)
