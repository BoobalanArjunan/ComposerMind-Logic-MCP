# v0.2.0 — Autonomous Audio Dataset Generator

Status: planned MVP, not released. Phase 1 locally validated on 2026-11-24 by the maintainer on an M1 Max: 8 unit tests passed; Logic detected; direct Python playback toggle visibly worked; Claude Code health check connected; independent Python MCP client initialized, discovered two tools and called logic_status with isError=False. MCP transport playback and transport-state readback remain unverified.

## One-day sprint (9 hours, conditional on UI compatibility)
- [ ] 1h: inspect Accessibility tree; create/select/rename tracks in disposable project.
- [ ] 1h: MIDI import and tempo control with readback.
- [ ] 2h: one stock synthesizer and one effect; verify parameter changes; use a prepared template if plugin insertion is unreliable.
- [ ] 1h: bounce to unique WAV path; verify file exists, decodes and has expected duration.
- [ ] 1h: integrate WaveWash via verified installed API/CLI; record version and results.
- [ ] 1h: seeded parameter variation, batch manifest, unique output paths and resumable jobs.
- [ ] 1h: bounded quality correction and retry; reject failures.
- [ ] 1h: run tests, document results and prepare release only if acceptance gates pass.

## MVP acceptance gates
1. Independent MCP client discovers tools and successfully invokes read-only status and guarded transport in a disposable project.
2. One synth/effect template produces at least one verified WAV without manual intervention after setup.
3. Ten consecutive renders complete with WAV and JSON provenance, no overwrites, and QA results; then attempt 100 accepted distinct sounds.
4. Demonstrate one deliberate quality failure and a bounded corrective retry; preserve failed attempts in manifest.
5. Report actual accepted count, wall time, failure rate and duplicate rate. If blocked, publish only tested functionality; 100 sounds is a stretch target, not a guarantee.

## Proposed tools
logic_open, logic_new_project, logic_save_project, logic_create_audio_track, logic_create_instrument_track, logic_rename_track, logic_select_track, logic_import_audio, logic_import_midi, logic_set_tempo, logic_load_plugin, logic_set_plugin_parameter, logic_bounce_audio, dataset_generate, dataset_status. Implement incrementally; only expose tested tools. Default mutations to dry-run or explicit opt-in. Verify UI focus and state; stop on unexpected dialogs. No destructive edits or overwrites. Use timeouts and bounded retries.

## Architecture
Structured recipe (later natural-language planner) -> deterministic parameter sampler -> MCP/Accessibility adapter -> Logic Pro template -> WAV bounce -> DSP/WaveWash QA -> accept or bounded parameter correction -> WAV + JSON + manifest. No Claude subscription required for Python batch execution. Logic UI automation is not headless; a logged-in macOS session and permissions are required. Universal AU control is not assumed.

## Metadata
Record recipe ID, seed, attempt, plugin names/versions, preset and parameter values, MIDI input, tempo, sample rate, bit depth, channels, duration, output hash, QA tool/version/results, timestamp, Logic version, code commit and status. Mark unknown values explicitly. Seeded recipes do not guarantee bit-identical plugin output.

## Research and innovation
MCP connectivity is infrastructure, not a novelty claim. Investigate semantic-to-parameter mapping, effect-chain selection, feedback-driven optimization, acoustic diversity and reproducible provenance. Compare random sampling vs feedback-guided sampling using matched budgets; report quality pass rate, acoustic diversity, duplicates, throughput, retries and reproducibility. Semantic accuracy requires independent evaluation. Review prior art before claiming novelty or patentability. Potential paper: An MCP-Driven Autonomous Audio Synthesis and Closed-Loop Quality Optimization Framework for Large-Scale Audio AI Dataset Generation.

## Beyond MVP
Generalized AU adapters, verified state readback, semantic planner, diversity optimization, crash recovery, larger 100,000-sample target, independent benchmarks and adoption. Verify plugin and source-content licenses before distributing datasets; do not publish proprietary presets or personal paths.
