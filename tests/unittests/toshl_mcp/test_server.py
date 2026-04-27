import toshl_mcp.server as server_module
from toshl_mcp.server import mcp


class TestToolRegistration:
    def test_all_tools_registered(self) -> None:
        tool_names = {t.name for t in mcp._tool_manager.list_tools()}
        expected = {
            "get_accounts",
            "get_entries",
            "get_categories",
            "get_tags",
            "get_budgets",
            "get_summary",
        }
        assert expected.issubset(tool_names)

    def test_tool_count(self) -> None:
        tools = mcp._tool_manager.list_tools()
        assert len(tools) >= 6


class TestGetClient:
    def test_raises_when_not_initialized(self) -> None:
        original = server_module._client
        try:
            server_module._client = None
            try:
                server_module._get_client()
                raise AssertionError("Should have raised")
            except RuntimeError as exc:
                assert "not initialized" in str(exc)
        finally:
            server_module._client = original
