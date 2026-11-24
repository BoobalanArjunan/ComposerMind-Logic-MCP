# Upstream integration (experimental)

ComposerMind now supports explicitly configured local MCP subprocesses. No upstream code is copied or bundled. Install upstream projects independently following their documentation and inspect/pin versions before use.

- rosa: https://github.com/rosasynthesiz/logic-pro-mcp (MIT), Python, includes OSC/MIDI/plugins/export.
- monglong: https://github.com/MongLong0214/logic-pro-mcp (MIT), Swift, project and MIDI operations.
- logician: https://github.com/BanneBanning/logician-mcp (MIT), Swift, rendering and audio feedback.
- Rubenknol: https://github.com/rubenknol/logic-pro-mcp, optional external backend; no source redistribution or modification pending permission. Use only an independently obtained installation you are authorized to run.

Create ~/.config/composermind/backends.json locally. Example (replace placeholders with installed executable paths):

```json
{
  "rosa": {"command": "/absolute/path/to/upstream/.venv/bin/logic-pro-mcp", "args": []},
  "monglong": {"command": "/absolute/path/to/LogicProMCP", "args": []},
  "logician": {"command": "/absolute/path/to/logician", "args": []},
  "rubenknol": {"command": "/absolute/path/to/node", "args": ["/absolute/path/to/rubenknol/dist/index.js"]}
}
```

For Logician verify the stdio command and arguments against its client installation guide. Use COMPOSERMIND_BACKENDS to override configuration location. Only configure trusted executables. Discover actual schemas with logic_backend_tools before calling logic_backend_call. Explicit execute=true is required for invocation. Raw upstream results are preserved; ComposerMind does not claim action verification. Start with a disposable Logic project and health/discovery only. Do not run other control-surface servers concurrently. The adapter currently starts a subprocess per request; persistent sessions, cross-request OSC/MCU lifecycle, serialization across simultaneous callers, and dataset orchestration remain unvalidated. macOS live testing is required; tests here are configuration/dry-run only. No automatic fallback or retries after writes.

Rubenknol requires its own Python worker environment (LOGIC_MCP_PYTHON) and IAC setup per upstream README. The current adapter does not inject backend-specific environment variables; configure them in the launching environment or a trusted local wrapper before testing. Do not start competing MCU surfaces concurrently.

## ComposerMind module aliases

| Module | Tool backend argument | Upstream configuration key |
|---|---|---|
| CM PluginCore | cm_plugincore | rosa |
| CM StudioCore | cm_studiocore | monglong |
| CM RenderCore | cm_rendercore | logician |
| CM MidiCore | cm_midicore | rubenknol |

CM ControlCore denotes the existing native ComposerMind tools. Aliases are integration branding only; upstream ownership and licensing remain unchanged. Existing configuration keys continue to work.
