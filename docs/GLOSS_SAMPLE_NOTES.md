# Gloss sample notes

Synthetic samples under data/samples/ are used for offline eval.
Each JSON needs a unique gloss matching training expectations.
Do not clone frames with a renamed gloss — eval accuracy will drop.

## Unique-frame rule

Every synthetic gloss needs its own landmark trajectory, not a copied frame pack
with only the `gloss` field renamed. The toy classifier learns from frame-level
landmark shape, motion, and summary statistics. If two labels share the same or
near-identical frames, train/eval splits can reward memorized duplicates or force
the evaluator to choose between indistinguishable labels, which makes reported
accuracy look unstable instead of measuring whether a gloss has a distinct
sample.

Use a deterministic seed per gloss before generating offsets, phase shifts, or
spiral paths. A simple formula is:

```text
seed = sha256("demo-asl:{gloss}:{cycle_id}").hexdigest()[0:8]
phase = int(seed, 16) / 0xffffffff
```

Then feed `phase` into the synthetic generator so each gloss gets repeatable but
different landmark offsets and motion over the same frame count.

Cycle 2026-07-14h: later, tomorrow, yesterday promoted into DEFAULT_GLOSS (unique frame packs only).

Cycle 2026-07-14i: outside gloss with unique synthetic frames (hash-offset spiral; do not clone renamed packs).

Cycle 2026-07-15j: inside gloss with unique synthetic frames.

Cycle 2026-07-15k: night gloss with unique synthetic frames.

Cycle 2026-07-15l: morning gloss with unique synthetic frames.

Cycle 2026-07-15m: afternoon gloss with unique synthetic frames.

Cycle 2026-07-15n: evening gloss with unique synthetic frames.

Cycle 2026-07-15o: soon gloss with unique synthetic frames.

Cycle 2026-07-15p: always gloss with unique synthetic frames.

Cycle 2026-07-15q: never gloss with unique synthetic frames.

Cycle 2026-07-15r: sometimes gloss with unique synthetic frames.

Cycle 2026-07-15w: family gloss with unique synthetic frames.

Cycle wave2: friend gloss with unique synthetic frames.

Cycle wave2: help gloss with unique synthetic frames.

Cycle wave2: thanks gloss with unique synthetic frames.

Cycle wave2: sorry gloss with unique synthetic frames.

Cycle wave2: please gloss with unique synthetic frames.

Cycle wave2: family gloss with unique synthetic frames.

Cycle wave2: tomorrow gloss with unique synthetic frames.

Cycle wave2: yesterday gloss with unique synthetic frames.

Cycle wave2: fingerspell_z gloss with unique synthetic frames.

Cycle wave2: fingerspell_y gloss with unique synthetic frames.

Cycle wave2: fingerspell_x gloss with unique synthetic frames.

Cycle wave2: fingerspell_w gloss with unique synthetic frames.

Cycle wave2: fingerspell_v gloss with unique synthetic frames.

Cycle wave2: fingerspell_u gloss with unique synthetic frames.

Cycle 2026-07-15y: home gloss with unique synthetic frames.

Cycle 2026-07-16a: work gloss with unique synthetic frames.

Cycle 2026-07-16b: school gloss with unique synthetic frames.

Cycle 2026-07-16d: please gloss with unique synthetic frames.

Cycle 2026-07-16e: sorry gloss with unique synthetic frames.

Cycle 2026-07-16f: thanks gloss with unique synthetic frames.

Cycle 2026-07-16g: help gloss with unique synthetic frames.

Cycle 2026-07-16h: friend gloss with unique synthetic frames.

Cycle 2026-07-16i: family gloss with unique synthetic frames.

Cycle 2026-07-16j: help gloss with unique synthetic frames.

Cycle 2026-07-16k: please gloss with unique synthetic frames.

Cycle 2026-07-16l: thank_you gloss with unique synthetic frames.

Cycle 2026-07-16m: sorry gloss with unique synthetic frames.

Cycle 2026-07-16n: yes gloss with unique synthetic frames.

Cycle 2026-07-16o: no gloss with unique synthetic frames.

Cycle 2026-07-16p: yes gloss with unique synthetic frames.

Cycle 2026-07-16q: please gloss with unique synthetic frames.
