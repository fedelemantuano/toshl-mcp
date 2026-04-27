# Toshl MCP

**Author:** Fedele Mantuano <mantuano.fedele@gmail.com>

MCP server that connects Claude Desktop to the [Toshl Finance API](https://developer.toshl.com/docs/).
Transport: stdio. Auth: Toshl Personal Token via HTTP Basic Auth.

## Tools

| Tool             | Description                                              |
| ---------------- | -------------------------------------------------------- |
| `get_accounts`   | List accounts with balances                              |
| `get_entries`    | List transactions with date range, category, tag filters |
| `get_categories` | List expense/income categories                           |
| `get_tags`       | List tags                                                |
| `get_budgets`    | List budgets with current spending status                |
| `get_summary`    | Aggregated stats (totals, averages) for a date range     |

## Requirements

- Python 3.13 or 3.14
- [uv](https://docs.astral.sh/uv/)
- Toshl Personal Token — generate at **Toshl → Profile → Apps & tokens**

## Installation

```bash
make install
```

## Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "toshl": {
      "command": "/path/to/uv",
      "args": [
        "--directory",
        "/path/to/toshl-mcp",
        "run",
        "toshl-mcp"
      ],
      "env": {
        "TOSHL_TOKEN": "<your-toshl-personal-token>"
      }
    }
  }
}
```

Replace `/path/to/uv` with the full path from `which uv` and `/path/to/toshl-mcp` with
the absolute path to this repository.

> **Note:** Use the full `uv` path (not just `uv`) — Claude Desktop may resolve `uv` to
> `uvx` which has different semantics and will fail to start the server.

## Environment Variables

| Variable      | Required | Default   | Description                                         |
| ------------- | -------- | --------- | --------------------------------------------------- |
| `TOSHL_TOKEN` | Yes      | —         | Toshl Personal Token                                |
| `LOG_LEVEL`   | No       | `WARNING` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

## Development

```bash
make lint        # check code
make lint-fix    # check and auto-fix
make format      # format code
make test        # run tests
make pre-commit  # run all pre-commit hooks
```

### Testing with MCP Inspector

The MCP Inspector lets you call tools interactively in a browser without Claude Desktop.

**1. Create a `.env` file** in the project root:

```bash
TOSHL_TOKEN=your-personal-token-here
```

**2. Start the inspector:**

```bash
make dev
```

**3. Open** `http://localhost:6274` in your browser.

**4. Connect** — click **Connect** in the top bar.

**5. Test tools:**

- Click **Tools** in the left sidebar
- Click **List Tools** to see all six tools
- Select a tool (e.g. `get_accounts`), fill in any parameters, click **Run**
