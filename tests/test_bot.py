import importlib
import json
import sys
import types

import pytest


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
    bot.get_rcon_server_info = lambda: None
    assert bot.get_server_info(process_output="") == {
        "name": "MyServer",
        "players": 5,
        "max_players": 20,
        "map": "my_map",
        "ping": round(0.123 * 1000, 2),
    }


@pytest.mark.parametrize("players", [0, 7])
def test_get_server_info_prefers_rcon_without_querying_a2s(players):
    def fake_info(addr, timeout=None):
        pytest.fail("A2S must not be queried when RCON succeeds")

    bot = import_bot_with_fakes(fake_info)
    bot.get_rcon_server_info = lambda: bot.parse_rcon_server_info(json.dumps({
        "Hostname": "MyServer",
        "Map": "my_map",
        "Players": players,
        "MaxPlayers": 30,
        "Queued": 3,
        "Joining": 2,
    }))

    assert bot.get_server_info(process_output="") == {
        "players": players,
        "max_players": 30,
        "queue": 3,
        "joining": 2,
    }


def test_get_server_info_falls_back_when_rcon_response_is_invalid():
    bot = import_bot_with_fakes(lambda addr, timeout=None: DummyInfo())
    bot.get_rcon_server_info = lambda: bot.parse_rcon_server_info(
        '{"Queued":3,"Joining":2}'
    )

    info = bot.get_server_info(process_output="")
    assert info == {
        "name": "MyServer",
        "players": 5,
        "max_players": 20,
        "map": "my_map",
        "ping": round(0.123 * 1000, 2),
    }
    assert bot.format_status_text(info) == "👥 5/20"


def test_get_server_info_returns_none_on_error():
    def fake_info(addr, timeout=None):
        raise RuntimeError("query failed")

    bot = import_bot_with_fakes(fake_info)
    bot.get_rcon_server_info = lambda: None
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


def test_parse_process_status_uses_starting_duration():
    bot = import_bot_with_fakes(lambda addr: DummyInfo())
    bot.STARTING_DURATION = 600
    output = "  400 ./RustDedicated -batchmode +app.listenip 0.0.0.0\n"

    assert bot.parse_process_status(output) == "starting"


def test_get_a2s_info_waits_between_retries(monkeypatch):
    attempts = []

    def fake_info(addr, timeout=None):
        attempts.append(addr)
        raise OSError("timed out")

    bot = import_bot_with_fakes(fake_info)
    sleeps = []
    monkeypatch.setattr(bot.time, "sleep", sleeps.append)

    assert bot.get_a2s_info(retries=3, delay=1) is None
    assert len(attempts) == 3
    assert sleeps == [1, 1]


def test_format_status_text_for_special_states():
    bot = import_bot_with_fakes(lambda addr: DummyInfo())

    assert bot.format_status_text(None) == "🔴 Offline"
    assert bot.format_status_text({"status": "wipe"}) == "🔧 Wipe in progress"
    assert bot.format_status_text({"status": "starting"}) == "⚙️ Starting"


def test_format_status_text_includes_queue_and_joining():
    bot = import_bot_with_fakes(lambda addr: DummyInfo())

    assert bot.format_status_text({
        "players": 5,
        "max_players": 20,
        "queue": 3,
        "joining": 2,
    }) == "👥 5/20 | Queue 3 | Joining 2"


def test_parse_rcon_server_info():
    bot = import_bot_with_fakes(lambda addr: DummyInfo())

    assert bot.parse_rcon_server_info(
        '{"Players":5,"MaxPlayers":20,"Queued":3,"Joining":2}'
    ) == {"players": 5, "max_players": 20, "queue": 3, "joining": 2}


@pytest.mark.parametrize("message", [
    "not json",
    "null",
    "[]",
    '{"Queued":3,"Joining":2}',
    '{"Players":"invalid","MaxPlayers":20,"Queued":3,"Joining":2}',
    '{"Players":"7","MaxPlayers":20,"Queued":3,"Joining":2}',
    '{"Players":7.9,"MaxPlayers":20,"Queued":3,"Joining":2}',
    '{"Players":true,"MaxPlayers":20,"Queued":3,"Joining":2}',
    '{"Players":null,"MaxPlayers":20,"Queued":3,"Joining":2}',
    '{"Players":Infinity,"MaxPlayers":20,"Queued":3,"Joining":2}',
    '{"Players":7,"MaxPlayers":20,"Queued":NaN,"Joining":2}',
])
def test_parse_rcon_server_info_rejects_invalid_counts(message):
    bot = import_bot_with_fakes(lambda addr: DummyInfo())

    assert bot.parse_rcon_server_info(message) is None


def test_get_rcon_server_info_requests_serverinfo():
    bot = import_bot_with_fakes(lambda addr: DummyInfo())
    bot.RCON_HOST = "127.0.0.1"
    bot.RCON_PORT = 28016
    bot.RCON_PASSWORD = "pass/word"
    bot.RCON_TIMEOUT = 4

    class FakeConnection:
        def __init__(self):
            self.sent = None
            self.closed = False

        def send(self, message):
            self.sent = json.loads(message)

        def recv(self):
            return json.dumps({
                "Identifier": 1001,
                "Message": '{"Players":7,"MaxPlayers":30,"Queued":3,"Joining":2}',
            })

        def close(self):
            self.closed = True

    connection = FakeConnection()

    def fake_connection_factory(url, timeout):
        assert url == "ws://127.0.0.1:28016/pass%2Fword"
        assert timeout == 4
        return connection

    assert bot.get_rcon_server_info(fake_connection_factory) == {
        "players": 7,
        "max_players": 30,
        "queue": 3,
        "joining": 2,
    }
    assert connection.sent == {
        "Identifier": 1001,
        "Message": "serverinfo",
        "Name": "WebRcon",
    }
    assert connection.closed is True


def test_get_server_info_falls_back_when_rcon_connection_fails():
    bot = import_bot_with_fakes(lambda addr, timeout=None: DummyInfo())
    bot.RCON_PASSWORD = "secret"

    def fake_connection_factory(url, timeout):
        raise OSError("connection refused")

    query_rcon = bot.get_rcon_server_info
    bot.get_rcon_server_info = lambda: query_rcon(fake_connection_factory)

    info = bot.get_server_info(process_output="")
    assert bot.format_status_text(info) == "👥 5/20"
