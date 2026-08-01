import importlib


def test_config_reads_env_vars(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "token")
    monkeypatch.setenv("CHANNEL_ID", "123")
    monkeypatch.setenv("RUST_SERVER_HOST", "1.2.3.4")
    monkeypatch.setenv("RUST_SERVER_PORT", "28018")
    monkeypatch.setenv("RCON_HOST", "5.6.7.8")
    monkeypatch.setenv("RCON_PORT", "28019")
    monkeypatch.setenv("RCON_PASSWORD", "secret")
    monkeypatch.setenv("RCON_TIMEOUT", "5")
    monkeypatch.setenv("UPDATE_INTERVAL", "60")

    import bot.config as config
    importlib.reload(config)

    assert config.DISCORD_TOKEN == "token"
    assert config.CHANNEL_ID == 123
    assert config.RUST_SERVER_HOST == "1.2.3.4"
    assert config.RUST_SERVER_PORT == 28018
    assert config.RCON_HOST == "5.6.7.8"
    assert config.RCON_PORT == 28019
    assert config.RCON_PASSWORD == "secret"
    assert config.RCON_TIMEOUT == 5
    assert config.UPDATE_INTERVAL == 60


def test_config_defaults(monkeypatch):
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    monkeypatch.delenv("CHANNEL_ID", raising=False)
    monkeypatch.delenv("RUST_SERVER_HOST", raising=False)
    monkeypatch.delenv("RUST_SERVER_PORT", raising=False)
    monkeypatch.delenv("RCON_HOST", raising=False)
    monkeypatch.delenv("RCON_PORT", raising=False)
    monkeypatch.delenv("RCON_PASSWORD", raising=False)
    monkeypatch.delenv("RCON_TIMEOUT", raising=False)
    monkeypatch.delenv("UPDATE_INTERVAL", raising=False)

    import bot.config as config
    importlib.reload(config)

    assert config.DISCORD_TOKEN is None
    assert config.CHANNEL_ID == 0
    assert config.RUST_SERVER_HOST == "127.0.0.1"
    assert config.RUST_SERVER_PORT == 28017
    assert config.RCON_HOST == "127.0.0.1"
    assert config.RCON_PORT == 28016
    assert config.RCON_PASSWORD is None
    assert config.RCON_TIMEOUT == 3
    assert config.UPDATE_INTERVAL == 30
