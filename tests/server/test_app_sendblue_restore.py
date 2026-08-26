"""Persisted channel bindings must preserve Ox Alpha's agent ban."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from openjarvis.server.app import _restore_sendblue_bindings


@pytest.mark.parametrize("model", ["openrouter/stealth/ox-alpha", "stealth/ox-alpha"])
@pytest.mark.parametrize("model_location", ["state", "engine"])
def test_restore_sendblue_skips_ox_alpha_before_connecting(model, model_location):
    manager = MagicMock()
    manager.list_agents.return_value = [
        {"id": "agent-1", "config": {"model": "gemma4:31b"}}
    ]
    manager.list_channel_bindings.return_value = [
        {
            "channel_type": "sendblue",
            "config": {
                "api_key_id": "key-id",
                "api_secret_key": "secret",
                "from_number": "+15551234567",
            },
        }
    ]
    app = SimpleNamespace(
        state=SimpleNamespace(
            agent_manager=manager,
            model=model if model_location == "state" else "local-model",
            engine=SimpleNamespace(
                _model=model if model_location == "engine" else "local-model"
            ),
        )
    )

    with patch("openjarvis.channels.sendblue.SendBlueChannel") as channel:
        _restore_sendblue_bindings(app)

    channel.assert_not_called()
    assert not hasattr(app.state, "sendblue_channel")
