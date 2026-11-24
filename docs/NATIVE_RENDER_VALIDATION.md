# Native RenderCore validation

User-reported live test, 2026-11-24, Logic Pro 11.2, Apple Silicon Mac.

Implementation commit: 99785d75a4b83b35943041a1ca4ae006420d1709.

Dry run returned executed=false, verified=false and the expected output path. A subsequent direct Python invocation of logic_bounce_audio with execute=True returned executed=true, verified=true, native_0002.wav, 48000 Hz, stereo, 24-bit PCM, duration 2.0 seconds, 577954 bytes.

This validates a single-call render from a prepared project with existing bounce settings. It does not establish unattended batch reliability, MCP protocol invocation, plugin parameter automation, acoustic diversity or WaveWash quality validation. The controller relies on foreground checks and timed keyboard events, not dialog identity verification. Use a disposable project and inspect the UI after failures.
