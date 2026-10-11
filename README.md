# Toshl MCP

[![PyPI - Version](https://img.shields.io/pypi/v/toshl-mcp)](https://pypi.org/project/toshl-mcp/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/toshl-mcp?color=blue)](https://pypistats.org/packages/toshl-mcp)

**Author:** [Fedele Mantuano](https://github.com/fedelemantuano)

MCP server that connects Codex, ChatGPT Desktop, Claude Desktop, and other
local MCP clients to the [Toshl Finance API](https://developer.toshl.com/docs/).
Transport: stdio. Auth: Toshl Personal Token via HTTP Basic Auth.

<video src="https://github.com/user-attachments/assets/a098586e-9711-46ae-a12a-8eb5f568403b" controls autoplay loop muted width="100%"></video>

## Tools

| Tool             | Description                                              |
| ---------------- | -------------------------------------------------------- |
| `get_accounts`   | List accounts with balances                              |
| `get_entries`    | List transactions with date range, category, tag filters |
| `get_categories` | List expense/income categories                           |
| `get_tags`       | List tags                                                |
| `get_budgets`    | List budgets with current spending status                |
| `get_summary`    | Toshl summary totals and averages for a date range       |

### `get_accounts`

Returns all Toshl accounts, including archived accounts. Each result includes
the account name, current and initial balances, currency, type, and status.

### `get_entries`

Returns transactions between the required inclusive `from_date` and `to_date`
arguments, both in `YYYY-MM-DD` format. The optional `category` argument filters
by category ID, while `tags` accepts comma-separated tag IDs.

Each entry includes its amount, currency, date, description, account, category,
and tags.

### `get_categories`

Returns expense and income categories. Use the optional `type` argument with
`expense` or `income` to return only that category type; omit it to return both.

Each category includes its ID, name, type, and deletion status.

### `get_tags`

Returns all user-defined Toshl tags. Each tag includes its ID, name, and whether
it applies to expenses or income.

### `get_budgets`

Returns all budgets with their limits and current spending status. Each budget
includes its ID, name, limit, amount spent, currency, and inclusive start and
end dates.

### `get_summary`

Returns expense and income aggregates from Toshl's summary endpoint. The
`from_date` and `to_date` arguments use `YYYY-MM-DD` and are both inclusive.
Use the optional `currency` argument to request a specific output currency;
when omitted, Toshl uses the user's main currency.

The result contains `from_date`, `to_date`, `total_expenses`, `total_income`,
`net`, `avg_daily_expense`, `period_days`, and `entry_count`. `entry_count`
combines Toshl's expense and income counts, and the daily average uses the
inclusive number of days in the range.

## Requirements

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/)
- Toshl Personal Token — generate at **Toshl → Profile → Apps & tokens**

## Installation

The examples below use macOS paths. Install the package once, then configure
each client that should use it.

**1. Install uv** (if not already installed):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**2. Install the package into a dedicated virtualenv:**

With uv:

```bash
uv venv ~/.toshl-mcp
uv pip install --python ~/.toshl-mcp/bin/python toshl-mcp
```

Or with pip:

```bash
python3 -m venv ~/.toshl-mcp
~/.toshl-mcp/bin/pip install toshl-mcp
```

### Codex CLI and IDE

Add the following to `~/.codex/config.toml`, keeping your existing settings:

```toml
[mcp_servers.toshl]
command = "/Users/<your-username>/.toshl-mcp/bin/toshl-mcp"

[mcp_servers.toshl.env]
TOSHL_TOKEN = "<your-toshl-personal-token>"
```

Replace `<your-username>` with your macOS username (run `whoami` to confirm)
and the token placeholder with your Toshl Personal Token. Keep this
configuration in your user directory; it contains your token.

Alternatively, register the same server with the CLI:

```bash
codex mcp add toshl \
  --env TOSHL_TOKEN="<your-toshl-personal-token>" \
  -- "$HOME/.toshl-mcp/bin/toshl-mcp"
```

Choose either the TOML configuration or the CLI command. Both configure the
same server. Codex CLI and the IDE extension share this configuration.
Start a new CLI session or restart the IDE extension after configuring it.

Verify registration:

```bash
codex mcp list
```

Then use `/mcp` in Codex CLI to check that `toshl` is connected. Registration
alone does not verify that the server starts or that the token is valid.

See the [official Codex MCP documentation](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).

### ChatGPT Desktop

For local Codex sessions in ChatGPT Desktop, use the same
`~/.codex/config.toml` configuration shown above. Desktop, Codex CLI, and the
IDE extension share MCP configuration on the same Codex host, so configuring
`toshl` once is sufficient.

To add the server through the Desktop interface instead:

1. Open **Settings → MCP servers → Add server**.
1. Enter `toshl` as the name and select **STDIO**.
1. Set the command to `/Users/<your-username>/.toshl-mcp/bin/toshl-mcp`.
1. Save the server.
1. Ensure the `[mcp_servers.toshl.env]` table in `~/.codex/config.toml`
   contains `TOSHL_TOKEN`, as shown above.
1. Save the TOML file and select **Restart** in the MCP settings.

Use `/mcp` in the composer to check that the server is connected. This setup
provides the local MCP server in the Codex host; ChatGPT web and hosted
Chat/Work conversations use their own plugin connections.

See the [official Desktop MCP documentation](https://learn.chatgpt.com/docs/extend/mcp?surface=app).

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "toshl": {
      "command": "/Users/<your-username>/.toshl-mcp/bin/toshl-mcp",
      "env": {
        "TOSHL_TOKEN": "<your-toshl-personal-token>"
      }
    }
  }
}
```

Replace `<your-username>` with your macOS username (run `whoami` to confirm).
Replace the token placeholder with your Toshl Personal Token, then restart
Claude Desktop.

### Verify the connection

After restarting your client, ask it to use Toshl's `get_categories` tool.
A successful tool response verifies both the MCP connection and Toshl
authentication. The server exposes all six tools listed above.

If the server fails to start, check the absolute executable path and that
`TOSHL_TOKEN` is set in the client configuration. The server reads environment
variables; installing the package does not configure a token automatically.

## Updating

Upgrade in place — use the same tool you installed with.

With uv:

```bash
uv pip install --python ~/.toshl-mcp/bin/python --upgrade toshl-mcp
```

Or with pip:

```bash
~/.toshl-mcp/bin/pip install --upgrade toshl-mcp
```

Then **restart the MCP server in each client that uses it**: start a new
Codex CLI session, restart the IDE extension, select **Restart** in ChatGPT
Desktop's MCP settings, or restart Claude Desktop. A running server process
keeps the old version until it is restarted.

Check the installed version:

```bash
~/.toshl-mcp/bin/python -c "import toshl_mcp; print(toshl_mcp.__version__)"
```

Compare it against the latest release on
[PyPI](https://pypi.org/project/toshl-mcp/).

Client configuration does not need to change — the path to the executable
stays the same across upgrades.

> **Note:** `uv venv` does not install `pip` into the virtualenv, so
> `~/.toshl-mcp/bin/pip` exists only if you used the pip install path.

## Environment Variables

| Variable      | Required | Default   | Description                                         |
| ------------- | -------- | --------- | --------------------------------------------------- |
| `TOSHL_TOKEN` | Yes      | —         | Toshl Personal Token                                |
| `LOG_LEVEL`   | No       | `WARNING` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

## Development

### Agent instructions

`CLAUDE.md` is the source of the repository instructions.
`AGENTS.md` is a relative symbolic link to `CLAUDE.md`, so Claude Code and
Codex read the same instructions. Edit `CLAUDE.md` to update both.

### Setup

**1. Install uv** (if not already installed):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**2. Install all dependencies:**

```bash
uv sync --all-groups
```

**3. Install pre-commit hooks:**

```bash
make pre-commit
```

### Make commands

```bash
make install     # install dependencies
make lint        # check code
make lint-fix    # check and auto-fix
make format      # format code
make test        # run tests
make test-cov    # run tests with coverage report
make pre-commit  # run all pre-commit hooks
make dev         # start MCP inspector (requires .env)
make clean       # remove build artifacts and caches
```

> **Note:** `make pre-commit` checks all tracked files, including unstaged changes.

### Testing with MCP Inspector

The MCP Inspector lets you call tools interactively in a browser.

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
