# Toshl MCP

**Author:** Fedele Mantuano <mantuano.fedele@gmail.com>

MCP server that connects Claude Desktop to the [Toshl Finance API](https://developer.toshl.com/docs/).
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
| `get_summary`    | Aggregated stats (totals, averages) for a date range     |

## Requirements

- Python 3.13 or 3.14
- [uv](https://docs.astral.sh/uv/)
- Toshl Personal Token — generate at **Toshl → Profile → Apps & tokens**

## Claude Desktop Configuration

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

**3. Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:**

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

## Environment Variables

| Variable      | Required | Default   | Description                                         |
| ------------- | -------- | --------- | --------------------------------------------------- |
| `TOSHL_TOKEN` | Yes      | —         | Toshl Personal Token                                |
| `LOG_LEVEL`   | No       | `WARNING` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

## Development

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

> **Note:** Stage changes with `git add` before running `make pre-commit` — unstaged files are ignored.

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
