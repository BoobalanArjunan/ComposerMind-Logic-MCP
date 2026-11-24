# Tempo validation — 2026-11-24

User-reported local prototype observations: native AX window discovery succeeded on attempt 1; tempo slider exposed AXIncrement and AXDecrement. Direct AXValue write from 120 toward 140 yielded 121. Coarse actions moved by 10 BPM; coarse-only control oscillated between 131 and 141.

Hybrid controller: 131 to 140 in 9 fine steps; 140 to 115 in 7 steps (2 coarse, 5 fine). Both final readbacks matched target. These observations concern the local experimental script, not yet the packaged bridge.

The integrated bridge accepts integer targets 40–240 as a conservative implementation limit, defaults to dry-run for writes, and stops on failed readback or non-convergence. Validate in a disposable project. A failed write may leave a partially changed tempo. No claim of universal AU parameter compatibility.

Integrated results (user-run on macOS): `python -m pytest -q` returned **22 passed in 0.02s**. Packaged `logic_get_tempo()` read **115 BPM**. Initial packaged `logic_set_tempo(128, execute=True)` failed with `Logic lost focus`; updated Swift bridge in commit `93b98b8` performs bounded focus reactivation and checks tempo consistency. After pulling this commit, user executed `logic_set_tempo(128, execute=True)` successfully: `{'initial_bpm': 115.0, 'bpm': 128.0, 'iterations': 4, 'executed': True, 'verified': True}`. This validates the Python-to-Swift integration for the target BPM 128 on this system. The MCP protocol endpoint for these new tools still needs independent end-to-end client testing.

Next: validate the MCP protocol tools from an MCP client, then implement MIDI import and project management.
