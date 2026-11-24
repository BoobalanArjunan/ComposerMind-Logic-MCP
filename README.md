# ComposerMind Logic MCP

A local-first Model Context Protocol (MCP) server for cautious, observable automation of Apple Logic Pro on macOS.

## Status

**Early prototype — not yet tested inside Logic Pro.** The first release includes read-only app diagnostics, a guarded transport command, and an explicit dry-run mode. It does **not** yet automate Audio Unit parameter editing, track creation, MIDI authoring, or bouncing.

## Requirements

- macOS with Logic Pro installed
- Python 3.10+
- macOS Automation consent for controlling Logic Pro (only needed for transport commands)
- An MCP-compatible client, such as Claude Desktop or Claude Code

## Install

```bash
git clone https://github.com/BoobalanArjunan/ComposerMind-Logic-MCP.git
cd ComposerMind-Logic-MCP
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python -m pytest
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
- `logic_transport(action, execute=False)` — prepares a play/stop/record command without changing the application unless `execute=True` is set; when executed, the command is sent with AppleScript to the Logic Pro application using an allowed keyboard shortcut

**Safety:** `record` is intentionally unavailable in this prototype. `play` and `stop` require opt-in execution. Be careful: Logic keyboard shortcuts are user-configurable and can differ by version; test in a disposable project. The prototype uses `tell application "Logic Pro" to activate` followed by `System Events` keystroke of the Space key; macOS Accessibility permissions may be required for the invoking program.

## Roadmap

1. Prove Logic launch detection, foreground activation, and play/stop commands on an M1 Max.
2. Build a Swift Accessibility bridge with stable, inspectable UI element targeting and read-back verification.
3. Add track creation and naming, supported audio imports, region selection, and undo-safe edits.
4. Add AU plugin identification and parameter controls where exposed through Accessibility; fall back to validated workflows.
5. Add bounce automation, render verification, and deterministic dataset recipes with WaveWash integration.

## License

MIT. Original project developed for ComposerMind Labs. Third-party libraries and plugins have their own licenses.
