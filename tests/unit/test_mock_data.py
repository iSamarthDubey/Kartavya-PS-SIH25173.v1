from assistant.mock_data import generate_mock_logs


def test_generate_mock_logs_uses_entities():
    entities = {"ip_address": ["203.0.113.5"], "user": ["alice"]}
    records = generate_mock_logs("failed_login", entities, limit=3)

    assert len(records) == 3
    for record in records:
        assert record["source.ip"] == "203.0.113.5"
        assert record["user.name"] == "alice"
        assert "failed" in record["message"].lower()


def test_generate_mock_logs_caps_limit():
    records = generate_mock_logs("network_analysis", {}, limit=500)

    assert len(records) == 100  # hard cap
    assert all("network" in rec["event.type"] for rec in records)
