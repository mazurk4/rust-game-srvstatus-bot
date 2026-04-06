import a2s
import discord
import asyncio
from .config import *

intents = discord.Intents.default()
client = discord.Client(intents=intents)


def get_server_info():
    try:
        info = a2s.info((RUST_SERVER_HOST, RUST_SERVER_PORT))
        return {
            "name": info.server_name,
            "players": info.player_count,
            "max_players": info.max_players,
            "map": info.map_name,
            "ping": round(info.ping * 1000, 2),
        }
    except Exception as e:
        print(f"[ERROR] {e}")
        return None


async def update_status():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    message = None

    while not client.is_closed():
        info = get_server_info()

        if info:
            content = (
                f"🎮 **{info['name']}**\n"
                f"👥 {info['players']} / {info['max_players']}\n"
                f"🗺️ {info['map']}\n"
                f"📡 {info['ping']} ms"
            )
        else:
            content = "❌ Server Offline"

        try:
            if message is None:
                message = await channel.send(content)
            else:
                await message.edit(content=content)
        except Exception as e:
            print(f"[DISCORD ERROR] {e}")
            message = None

        await asyncio.sleep(UPDATE_INTERVAL)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    client.loop.create_task(update_status())


client.run(DISCORD_TOKEN)