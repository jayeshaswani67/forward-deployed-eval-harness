from unittest.mock import MagicMock
from app.agent import RetrievalAgent, AgentOutput

def test_agent_fallback_on_api_error():
    """Validates that agent returns safe deterministic fallback if upstream API errors out."""
    mock_client = MagicMock()
    mock_client.beta.chat.completions.parse.side_effect = RuntimeError("OpenAI 503 Service Unavailable")

    agent = RetrievalAgent(client=mock_client)
    res = agent.query("What is the refund policy?")

    assert isinstance(res, AgentOutput)
    assert "Error processing query" in res.answer
    assert res.confidence == 0.0
    assert res.metadata.get("fallback_triggered") is True