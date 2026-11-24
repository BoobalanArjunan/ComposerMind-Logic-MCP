# ComposerMind Logic MCP

A local-first Model Context Protocol (MCP) server for cautious, observable automation of Apple Logic Pro on macOS.

## Status

**v0.1.0 — locally validated prototype.** Maintainer reports 8 passing unit tests, visible direct Python playback toggle, successful Claude Code connection health check and independent Python MCP status call. Track creation, AU edits and rendering are not implemented. See the [roadmap](docs/ROADMAP.md) for the planned autonomous dataset MVP.

## Requirements

- macOS with Logic Pro installed
- Python 3.10+
- macOS Automation consent for controlling Logic Pro (only needed for transport commands)
- An MCP-compatible client, such as Claude Desktop or Claude Code

## Install

```bash
git clone https://github.com/BoobalanArjunan/ComposerMind-Logic-MCP.git
cd ComposerMind-Logic-MCP
git switch feat/logic-mcp-prototype
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
PYTHONPATH="$PWD/src" python -m pytest -q
```

## Run

```bash
composer-logic-mcp
```

MCP clients can launch the executable with stdio transport. Example Claude Desktop `mcpServers` configuration (replace the path):

```json
{
  "mcpServers": {
    "composer-logic": {
      "command": "/absolute/path/to/ComposerMind-Logic-MCP/.venv/bin/composer-logic-mcp"
    }
  }
}
```

## Tools

- `logic_status()` — checks that the platform is macOS, whether Logic Pro is installed and whether it is currently running
- `logic_transport(action, execute=False)` — prepares a playback toggle without changing the application unless `execute=True` is set; when executed, the command is sent with AppleScript to the Logic Pro application using an allowed keyboard shortcut

**Safety:** `record` is intentionally unavailable in this prototype. Only `toggle_playback` is supported; execution requires explicit opt-in and does not verify transport state. Be careful: Logic keyboard shortcuts are user-configurable and can differ by version; test in a disposable project. The prototype uses `tell application "Logic Pro" to activate` followed by `System Events` keystroke of the Space key; macOS Accessibility permissions may be required for the invoking program.

## Roadmap

See the [one-day MVP and research roadmap](docs/ROADMAP.md). The target is a quality-aware dataset generator using a single verified synth/effect workflow before expanding plugin coverage.

## License

MIT. Original project developed for ComposerMind Labs. Third-party libraries and plugins have their own licenses.

## Tested local startup

```bash
PYTHONPATH="$PWD/src" "$PWD/.venv/bin/python" -m composer_logic_mcp.server
```

MCP SDK 1.x is required. A silent server waits for stdio requests. Stop with Ctrl+C before registering Claude Code:

```bash
claude mcp add --scope user composer-logic -- /usr/bin/env "PYTHONPATH=$PWD/src" "$PWD/.venv/bin/python" -m composer_logic_mcp.server
claude mcp list
```

Claude login is optional for independent Python MCP testing.
