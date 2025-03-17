import pytest


@pytest.mark.anyio
async def test_slack_api_apps_connections_open(bot):
    await bot.api.apps.connections.open(token="TEST_TOKEN")  # noqa: S106
    call = bot.call_queue.pop()
    assert call.method == "apps.connections.open"
    assert call.data == {}
    assert call.token == "TEST_TOKEN"  # noqa: S105
