# ComposerMind Logic MCP

A local-first Model Context Protocol (MCP) server for cautious, observable automation of Apple Logic Pro on macOS.

## Status

**Early prototype — not yet tested inside Logic Pro.** The first release contains read-only diagnostics, an explicitly opted-in playback toggle and dry-run mode. The prototype does **not** yet implement AU parameter edits, track creation, MIDI authoring or bounce automation.

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
pytest -q
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

1. Verify diagnostics and keyboard toggle on the M1 Max.
2. Add a Swift Accessibility bridge with read-back checks and transport state verification.
3. Implement observable track creation, naming, audio import and undo behavior.
4. Explore AU plugin identification and parameter editing, subject to accessibility exposure.
5. Add bounce verification, deterministic dataset recipes, batch job recovery and WaveWash QA.

## License

MIT. Third-party libraries, apps and AU plugins are licensed separately.
