# Upstream integration (experimental)

ComposerMind now supports explicitly configured local MCP subprocesses. No upstream code is copied or bundled. Install upstream projects independently following their documentation and inspect/pin versions before use.

- rosa: https://github.com/rosasynthesiz/logic-pro-mcp (MIT), Python, includes OSC/MIDI/plugins/export.
- monglong: https://github.com/MongLong0214/logic-pro-mcp (MIT), Swift, project and MIDI operations.
- logician: https://github.com/BanneBanning/logician-mcp (MIT), Swift, rendering and audio feedback.
- Rubenknol: https://github.com/rubenknol/logic-pro-mcp, reference only pending permission. Not enabled.

Create ~/.config/composermind/backends.json locally. Example (replace placeholders with installed executable paths):

```json
{
  "rosa": {"command": "/absolute/path/to/upstream/.venv/bin/logic-pro-mcp", "args": []},
  "monglong": {"command": "/absolute/path/to/LogicProMCP", "args": []},
  "logician": {"command": "/absolute/path/to/logician", "args": []}
}
```

For Logician verify the stdio command and arguments against its client installation guide. Use COMPOSERMIND_BACKENDS to override configuration location. Only configure trusted executables. Discover actual schemas with logic_backend_tools before calling logic_backend_call. Explicit execute=true is required for invocation. Raw upstream results are preserved; ComposerMind does not claim action verification. Start with a disposable Logic project and health/discovery only. Do not run other control-surface servers concurrently. The adapter currently starts a subprocess per request; persistent sessions, cross-request OSC/MCU lifecycle, serialization across simultaneous callers, and dataset orchestration remain unvalidated. macOS live testing is required; tests here are configuration/dry-run only. No automatic fallback or retries after writes.
