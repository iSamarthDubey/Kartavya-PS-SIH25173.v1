import pytest

from assistant.pipeline import ConversationalPipeline


class EmptyConnector:
    async def search(self, *args, **kwargs):
        return {"hits": []}


@pytest.mark.asyncio
async def test_pipeline_uses_mock_data_when_no_sources(monkeypatch):
    pipeline = ConversationalPipeline()
    await pipeline.initialize()

    pipeline.elastic_connector = EmptyConnector()
    pipeline.wazuh_connector = EmptyConnector()

    result = await pipeline.process_query("Show failed login attempts")

    assert result["status"] == "success"
    assert result["metadata"]["mock_data"] is True
    assert result["metadata"]["results_count"] == len(result["results"])
    assert "mock-data" in result["metadata"]["data_sources"]
    assert result["results"]
