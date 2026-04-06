import a2s
import discord
import asyncio
import socket
from .config import *

intents = discord.Intents.default()
client = discord.Client(intents=intents)


def get_server_info():
    try:
        info = a2s.info((RUST_SERVER_HOST, RUST_SERVER_PORT), timeout=3)
        return {
            "online": True,
            "players": info.player_count,
            "max_players": info.max_players,
        }
    except (socket.timeout, ConnectionRefusedError, OSError):
        return {
            "online": False,
            "players": 0,
            "max_players": 0,
        }
    except Exception as e:
        print(f"[ERROR] {e}")
        return {
            "online": False,
            "players": 0,
            "max_players": 0,
        }


async def update_status():
    await client.wait_until_ready()

    print("Status loop started")

    while not client.is_closed():
        loop = asyncio.get_event_loop()
        status = await loop.run_in_executor(None, get_server_info)

        if status["online"]:
            text = f"👥 {status['players']}/{status['max_players']}"
        else:
            text = "🔴 Offline"

        try:
            await client.change_presence(
                status=discord.Status.online,
                activity=discord.Game(name=text)
            )
            print(f"[UPDATE] {text}")
        except Exception as e:
            print(f"[DISCORD ERROR] {e}")

        await asyncio.sleep(UPDATE_INTERVAL)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    client.loop.create_task(update_status())


client.run(DISCORD_TOKEN)