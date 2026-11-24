# Tempo validation — 2026-11-24

User-reported local prototype observations: native AX window discovery succeeded on attempt 1; tempo slider exposed AXIncrement and AXDecrement. Direct AXValue write from 120 toward 140 yielded 121. Coarse actions moved by 10 BPM; coarse-only control oscillated between 131 and 141.

Hybrid controller: 131 to 140 in 9 fine steps; 140 to 115 in 7 steps (2 coarse, 5 fine). Both final readbacks matched target. These observations concern the local experimental script, not yet the packaged bridge.

The integrated bridge accepts integer targets 40–240 as a conservative implementation limit, defaults to dry-run for writes, and stops on failed readback or non-convergence. Validate in a disposable project. A failed write may leave a partially changed tempo. No claim of universal AU parameter compatibility.

Next: pull branch, run pytest, test packaged get/set tools locally and via MCP, then MIDI import.
