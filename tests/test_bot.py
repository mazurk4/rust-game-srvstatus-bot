import importlib
import sys
import types


class DummyInfo:
    server_name = "MyServer"
    player_count = 5
    max_players = 20
    map_name = "my_map"
    ping = 0.123


class FakeIntents:
    @staticmethod
    def default():
        return object()


class FakeClient:
    def __init__(self, intents):
        self.intents = intents
        self.loop = types.SimpleNamespace(create_task=lambda *args, **kwargs: None)

    def event(self, func):
        return func

    async def wait_until_ready(self):
        return None

    def is_closed(self):
        return True

    def get_channel(self, channel_id):
        return None

    def run(self, token):
        return None


def import_bot_with_fakes(fake_info):
    fake_a2s = types.SimpleNamespace(info=fake_info)
    fake_discord = types.ModuleType("discord")
    fake_discord.Intents = FakeIntents
    fake_discord.Client = FakeClient

    sys.modules["a2s"] = fake_a2s
    sys.modules["discord"] = fake_discord

    import bot.bot as bot
    importlib.reload(bot)
    return bot


def test_get_server_info_returns_parsed_data():
    def fake_info(addr, timeout=None):
        assert addr == ("127.0.0.1", 28017)
        assert timeout == 3
        return DummyInfo()

    bot = import_bot_with_fakes(fake_info)
    assert bot.get_server_info(process_output="") == {
        "name": "MyServer",
        "players": 5,
        "max_players": 20,
        "map": "my_map",
        "ping": round(0.123 * 1000, 2),
    }


def test_get_server_info_returns_none_on_error():
    def fake_info(addr, timeout=None):
        raise RuntimeError("query failed")

    bot = import_bot_with_fakes(fake_info)
    assert bot.get_server_info(process_output="") is None


def test_parse_process_status_returns_wipe_when_wipe_process_exists():
    bot = import_bot_with_fakes(lambda addr: DummyInfo())
    output = "  120 sh -c /home/rustgsmadm/wipe.sh\n"

    assert bot.parse_process_status(output) == "wipe"


def test_parse_process_status_returns_starting_when_rustdedicated_started_recently():
    bot = import_bot_with_fakes(lambda addr: DummyInfo())
    output = "  250 ./RustDedicated -batchmode +app.listenip 0.0.0.0\n"

    assert bot.parse_process_status(output) == "starting"


def test_parse_process_status_returns_none_when_rustdedicated_is_old():
    bot = import_bot_with_fakes(lambda addr: DummyInfo())
    output = "  400 ./RustDedicated -batchmode +app.listenip 0.0.0.0\n"

    assert bot.parse_process_status(output) is None


def test_format_status_text_for_special_states():
    bot = import_bot_with_fakes(lambda addr: DummyInfo())

    assert bot.format_status_text(None) == "🔴 Offline"
    assert bot.format_status_text({"status": "wipe"}) == "🔧 Wipe in progress"
    assert bot.format_status_text({"status": "starting"}) == "⚙️ Starting"
