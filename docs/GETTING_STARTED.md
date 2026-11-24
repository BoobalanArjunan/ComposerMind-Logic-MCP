# ComposerMind Logic MCP

A local-first Model Context Protocol (MCP) server for cautious, observable automation of Apple Logic Pro on macOS.

## Status

**v0.1.0 — locally validated prototype.** Maintainer reports 8 passing unit tests, visible direct Python playback toggle, successful Claude Code connection health check and independent Python MCP status call. Track creation, AU edits and rendering are not implemented. See the [roadmap](ROADMAP.md) for the planned autonomous dataset MVP.

## Requirements

- macOS with Logic Pro installed
- Python 3.10+
- macOS Automation / Accessibility permissions for the app launching the server when invoking the playback toggle
- MCP-compatible client such as Claude Desktop or Claude Code

## Install and test

```bash
git clone https://github.com/BoobalanArjunan/ComposerMind-Logic-MCP.git
cd ComposerMind-Logic-MCP
git switch feat/logic-mcp-prototype
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
PYTHONPATH="$PWD/src" python -m pytest -q
```

## Run

```bash
composer-logic-mcp
```

MCP clients should launch the command through their stdio transport. Example Claude Desktop `mcpServers` setting (replace the path):

```json
{
  "mcpServers": {
    "composer-logic": {
      "command": "/absolute/path/to/ComposerMind-Logic-MCP/.venv/bin/composer-logic-mcp"
    }
  }
}
```

## Available tools

- `logic_status()`: checks macOS, app installation and running state, without changing Logic.
- `logic_transport(action="toggle_playback", execute=False)`: dry-run by default. With `execute=True`, activates Logic Pro and sends the standard Space shortcut. This is a **toggle**, not a guaranteed play or stop command. It does not verify whether playback started or stopped.

The first version deliberately rejects recording, editing and rendering calls.

## Safety and limitations

Test only in a disposable Logic project, after saving your work. The user may have customized keyboard commands. Sending the Space shortcut requires Logic to be accessible and macOS permissions for the controlling program. The initial app process check is best-effort, not a security guarantee. No network server or authentication is provided: MCP communicates over local stdio.

## Roadmap

See the [one-day MVP and research roadmap](ROADMAP.md). The target is a quality-aware dataset generator using a single verified synth/effect workflow before expanding plugin coverage.

## License

MIT. Third-party libraries, apps and AU plugins are licensed separately.

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
