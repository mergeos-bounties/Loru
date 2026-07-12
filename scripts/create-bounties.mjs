import { execSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

const REPO = 'mergeos-bounties/Loru';

function sh(cmd) {
  return execSync(cmd, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim();
}

function ensureLabel(name, color, description) {
  try {
    sh(
      `gh label create ${JSON.stringify(name)} --repo ${REPO} --color ${color} --description ${JSON.stringify(description)}`,
    );
  } catch {
    try {
      sh(
        `gh label edit ${JSON.stringify(name)} --repo ${REPO} --color ${color} --description ${JSON.stringify(description)}`,
      );
    } catch {
      // ignore
    }
  }
}

function createIssue(title, body, labels) {
  const dir = mkdtempSync(join(tmpdir(), 'loru-issue-'));
  const file = join(dir, 'body.md');
  try {
    writeFileSync(file, body, 'utf8');
    const labelFlags = labels.map((l) => `--label ${JSON.stringify(l)}`).join(' ');
    const out = sh(
      `gh issue create --repo ${REPO} --title ${JSON.stringify(title)} --body-file ${JSON.stringify(file)} ${labelFlags}`,
    );
    console.log(out);
    return out;
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

const labels = [
  ['bounty', '5319E7', 'Eligible for MergeOS MRG bounty'],
  ['bounty: feature', 'A2EEEF', 'Feature bounty'],
  ['bounty: bug', 'D73A4A', 'Bug bounty'],
  ['ml', 'B60205', 'Models / training / evaluation'],
  ['data', 'C5DEF5', 'Datasets / loaders / annotation'],
  ['voice', 'D4C5F9', 'TTS / sign-to-voice'],
  ['api', '1D76DB', 'HTTP / websocket API'],
  ['accessibility', '0E8A16', 'A11y / sign-language UX'],
  ['reward:25-mrg', 'FEF2C0', 'Target 25 MRG'],
  ['reward:50-mrg', 'FEF2C0', 'Target 50 MRG'],
  ['reward:100-mrg', 'FEF2C0', 'Target 100 MRG'],
  ['reward:200-mrg', 'FEF2C0', 'Target 200 MRG'],
  ['good first issue', '7057FF', 'Good for newcomers'],
  ['documentation', '0075CA', 'Documentation improvements'],
];

for (const [name, color, description] of labels) {
  ensureLabel(name, color, description);
}

const footer = `

## Claim (MergeOS MRG)

1. Star https://github.com/mergeos-bounties/Loru and https://github.com/mergeos-bounties/mergeos  
2. Comment on **this issue**: \`I claim this bounty\`  
3. Comment on MergeOS [Claim Token #1](https://github.com/mergeos-bounties/mergeos/issues/1) with a link to this issue  
4. Open a PR to **Loru** with \`Fixes #<this-issue>\`

Policy: [docs/BOUNTY.md](../blob/master/docs/BOUNTY.md)

## Payout

Maintainer reviews PR → merge on Loru → **MRG credit** on MergeOS ledger to \`github:<author>\` (25/50/100/200 scale).
`;

const issues = [
  {
    title: '[25 MRG] Docs: DATASETS.md catalog of public sign corpora + licenses',
    labels: ['bounty', 'bounty: feature', 'documentation', 'data', 'reward:25-mrg', 'good first issue'],
    body: `## Bounty: 25 MRG

Create \`docs/DATASETS.md\` listing public sign-language datasets (WLASL, MS-ASL, How2Sign, Phoenix-2014T, etc.) with:
- License summary
- Language / size
- Whether video or landmarks
- Link + citation
- Safe-to-use notes for open-source training

Do **not** redistributing copyrighted media; document only.

## Acceptance

- [ ] \`docs/DATASETS.md\` merged with ≥8 corpora rows
- [ ] Each row has license + link
- [ ] Ethics note matches README
${footer}`,
  },
  {
    title: '[25 MRG] CLI: loru eval toy — accuracy table over data/samples',
    labels: ['bounty', 'bounty: feature', 'ml', 'reward:25-mrg', 'good first issue'],
    body: `## Bounty: 25 MRG

Add \`loru eval toy\` that loads the demo classifier, runs every sample, prints a rich table (gloss / pred / conf / ok), and exit code 0 when accuracy ≥ 0.8.

## Acceptance

- [ ] Command registered in \`cli.py\`
- [ ] Unit test with samples
- [ ] README documents the command
${footer}`,
  },
  {
    title: '[25 MRG] Gloss vocab: load from YAML/JSON + expand DEFAULT_GLOSS',
    labels: ['bounty', 'bounty: feature', 'ml', 'data', 'reward:25-mrg', 'good first issue'],
    body: `## Bounty: 25 MRG

Make gloss vocabulary configurable via \`data/vocab.json\` (or YAML) with fallback to \`DEFAULT_GLOSS\`. Support add/list CLI helpers.

## Acceptance

- [ ] \`loru vocab list\` works
- [ ] Custom vocab file loaded when present
- [ ] Tests cover missing + present files
${footer}`,
  },
  {
    title: '[25 MRG] Sequence schema validation with pydantic',
    labels: ['bounty', 'bounty: feature', 'data', 'reward:25-mrg', 'good first issue'],
    body: `## Bounty: 25 MRG

Define a pydantic model for sample JSON (\`gloss\`, \`frames\`, optional \`fps\`, \`language\`) and validate in the loader. Clear errors for bad shapes.

## Acceptance

- [ ] Invalid sample raises helpful error
- [ ] Existing samples validate
- [ ] Tests for good/bad payloads
${footer}`,
  },
  {
    title: '[50 MRG] MediaPipe Holistic landmark extractor adapter',
    labels: ['bounty', 'bounty: feature', 'ml', 'data', 'reward:50-mrg'],
    body: `## Bounty: 50 MRG

Add \`src/loru/data/mediapipe_extract.py\` (optional dep) that turns a video path into Loru sample JSON (hands + pose landmarks). Document install extras.

## Acceptance

- [ ] CLI: \`loru data extract --video <path> --out data/samples/custom.json\`
- [ ] Graceful error if mediapipe not installed
- [ ] Unit test with a tiny synthetic/mock path OR skip-marked integration test
- [ ] No large videos committed
${footer}`,
  },
  {
    title: '[50 MRG] Dataset adapter: WLASL-style index → Loru sequences',
    labels: ['bounty', 'bounty: feature', 'data', 'ml', 'reward:50-mrg'],
    body: `## Bounty: 50 MRG

Implement a loader that reads a WLASL (or similar) **index JSON** and maps entries into Loru-compatible manifests. Download is out of scope unless offline fixture provided.

## Acceptance

- [ ] Adapter module + CLI or script
- [ ] Fixture index under \`tests/fixtures/\`
- [ ] License notes in PR body
${footer}`,
  },
  {
    title: '[50 MRG] Sign→text: sequence model baseline (CTC or tiny transformer stub)',
    labels: ['bounty', 'bounty: feature', 'ml', 'reward:50-mrg'],
    body: `## Bounty: 50 MRG

Replace pure prototype matching with a real sequence baseline under optional \`torch\` extra. Keep toy model as fallback.

## Acceptance

- [ ] Train script + checkpoint save/load API
- [ ] Infer path can load checkpoint when present
- [ ] Tests run without GPU; CPU or skip if torch missing
- [ ] Document in README
${footer}`,
  },
  {
    title: '[50 MRG] Metrics: top-k accuracy, confusion matrix, report JSON',
    labels: ['bounty', 'bounty: feature', 'ml', 'reward:50-mrg'],
    body: `## Bounty: 50 MRG

Add evaluation metrics module + CLI export for confusion matrix and top-k accuracy over samples or a held-out split.

## Acceptance

- [ ] \`loru eval report --out data/runs/metrics.json\`
- [ ] Tests for top-1 / top-k helpers
- [ ] Matrix printable via rich
${footer}`,
  },
  {
    title: '[50 MRG] Sign→voice: pyttsx3 or edge-tts real backend',
    labels: ['bounty', 'bounty: feature', 'voice', 'reward:50-mrg'],
    body: `## Bounty: 50 MRG

Implement a real TTS backend behind \`TextToSpeech\` (pyttsx3 and/or edge-tts). Keep offline stub as default when deps missing.

## Acceptance

- [ ] \`get_default_tts()\` selects real engine when available
- [ ] WAV or MP3 written with audible speech when engine works
- [ ] CI still green without optional voice deps (stub path)
- [ ] README documents extras
${footer}`,
  },
  {
    title: '[50 MRG] FastAPI: POST /infer/text and /infer/voice',
    labels: ['bounty', 'bounty: feature', 'api', 'reward:50-mrg'],
    body: `## Bounty: 50 MRG

Ship optional FastAPI app under \`src/loru/api/\` with:
- \`POST /infer/text\` (JSON sequence body)
- \`POST /infer/voice\` (returns path or audio bytes)
- \`GET /health\`

## Acceptance

- [ ] \`loru serve\` or uvicorn entry documented
- [ ] Tests with TestClient (api extra)
- [ ] OpenAPI tags clean
${footer}`,
  },
  {
    title: '[50 MRG] Gloss→sentence: template pack + simple NLG for multi-gloss',
    labels: ['bounty', 'bounty: feature', 'ml', 'reward:50-mrg'],
    body: `## Bounty: 50 MRG

Expand \`gloss_to_sentence\` to multi-gloss sequences (e.g. HELLO + NAME) with templates or a tiny rule-based NLG. Support EN + optional VI stubs.

## Acceptance

- [ ] Multi-gloss API + tests
- [ ] At least EN full coverage for DEFAULT_GLOSS
- [ ] Document extension format
${footer}`,
  },
  {
    title: '[50 MRG] Webcam demo: OpenCV capture loop → live gloss print',
    labels: ['bounty', 'bounty: feature', 'ml', 'accessibility', 'reward:50-mrg'],
    body: `## Bounty: 50 MRG

CLI \`loru infer webcam\` that opens a camera (when available), extracts landmarks (or mock), and prints predicted gloss at ~FPS. Headless CI must skip gracefully.

## Acceptance

- [ ] Command exists + documented
- [ ] No crash when no camera (clear message)
- [ ] Optional: save last N frames as sample JSON
${footer}`,
  },
  {
    title: '[100 MRG] Continuous signing: sliding window + gloss stream',
    labels: ['bounty', 'bounty: feature', 'ml', 'reward:100-mrg'],
    body: `## Bounty: 100 MRG

Move beyond isolated signs: implement a sliding-window recognizer that emits a stream of glosses with confidence + debounce (no spam).

## Acceptance

- [ ] Stream API or CLI mode
- [ ] Debounce / hysteresis documented
- [ ] Tests with synthetic multi-sign sequences
${footer}`,
  },
  {
    title: '[100 MRG] Vietnamese Sign Language (VSL) pilot pack',
    labels: ['bounty', 'bounty: feature', 'data', 'accessibility', 'reward:100-mrg'],
    body: `## Bounty: 100 MRG

Add a **VSL pilot**: vocab list, sample sequences (synthetic or consented), VI templates for sign→text, and docs on VSL resources.

## Acceptance

- [ ] \`data/samples/vsl/\` or language tag on samples
- [ ] Vocab + templates for ≥15 glosses
- [ ] Ethics + data provenance in docs
- [ ] Tests cover VSL path
${footer}`,
  },
  {
    title: '[100 MRG] Browser webcam UI for sign→text demo',
    labels: ['bounty', 'bounty: feature', 'api', 'accessibility', 'reward:100-mrg'],
    body: `## Bounty: 100 MRG

Static or light frontend (Vite/vanilla) that streams webcam landmarks (MediaPipe JS or server path) and shows live text. Ship under \`web/\` or \`frontend/\`.

## Acceptance

- [ ] Local dev README
- [ ] Screenshot evidence in PR
- [ ] No secrets; works with local Loru API when available
${footer}`,
  },
  {
    title: '[100 MRG] Training pipeline: config YAML + seed + checkpoint resume',
    labels: ['bounty', 'bounty: feature', 'ml', 'reward:100-mrg'],
    body: `## Bounty: 100 MRG

Production-shaped training loop: hydra-like or plain YAML configs, seed control, early stopping stub, checkpoint resume, tensorboard optional.

## Acceptance

- [ ] \`configs/toy.yaml\` example
- [ ] CLI train with config path
- [ ] Resume from checkpoint tested
- [ ] Docs for contributors
${footer}`,
  },
  {
    title: '[200 MRG] End-to-end product path: video → text → voice with demo video',
    labels: ['bounty', 'bounty: feature', 'ml', 'voice', 'accessibility', 'reward:200-mrg'],
    body: `## Bounty: 200 MRG

Ship a polished E2E demo: sample video (consented/short) → landmarks → text → TTS audio, one command, documented quality bar.

## Acceptance

- [ ] Single CLI or notebook path
- [ ] Short demo assets under license-safe terms
- [ ] Accuracy notes + known limitations
- [ ] Evidence: command log + audio sample + optional screen capture
${footer}`,
  },
  {
    title: '[25 MRG] CI polish: coverage badge + ruff format check',
    labels: ['bounty', 'bounty: feature', 'documentation', 'reward:25-mrg', 'good first issue'],
    body: `## Bounty: 25 MRG

Improve \`.github/workflows/ci.yml\`: pytest-cov threshold (reasonable), \`ruff format --check\`, cache pip.

## Acceptance

- [ ] CI green on PR
- [ ] README badge optional
${footer}`,
  },
  {
    title: '[25 MRG] CONTRIBUTING.md + good-first-issue path for Loru',
    labels: ['bounty', 'bounty: feature', 'documentation', 'reward:25-mrg', 'good first issue'],
    body: `## Bounty: 25 MRG

Write \`CONTRIBUTING.md\` with setup, test commands, PR checklist, and link to MergeOS claim flow.

## Acceptance

- [ ] File merged + linked from README
${footer}`,
  },
  {
    title: '[50 MRG] Landmark augmentation: noise, time warp, drop frames',
    labels: ['bounty', 'bounty: feature', 'ml', 'data', 'reward:50-mrg'],
    body: `## Bounty: 50 MRG

Augmentation helpers for landmark sequences to toughen toy/real training. CLI flag or train-time hook.

## Acceptance

- [ ] Module + unit tests proving shape preservation
- [ ] Optional use in \`train toy\`
${footer}`,
  },
  {
    title: '[50 MRG] Export ONNX (or torchscript) for toy/sequence model',
    labels: ['bounty', 'bounty: feature', 'ml', 'reward:50-mrg'],
    body: `## Bounty: 50 MRG

Export path for inference outside Python training env. Prefer ONNX if torch available.

## Acceptance

- [ ] Export CLI
- [ ] Load + predict parity test (or skip if no torch)
- [ ] Docs
${footer}`,
  },
  {
    title: '[50 MRG] Accessibility docs: how deaf/hard-of-hearing users benefit + safety',
    labels: ['bounty', 'bounty: feature', 'documentation', 'accessibility', 'reward:50-mrg'],
    body: `## Bounty: 50 MRG

Write \`docs/ACCESSIBILITY.md\`: intended users, limitations of automated SLR, consent, when human interpreters are required.

## Acceptance

- [ ] Doc merged + README link
- [ ] Clear non-claims / safety language
${footer}`,
  },
];

for (const issue of issues) {
  createIssue(issue.title, issue.body, issue.labels);
}

console.log(`Created ${issues.length} issues on ${REPO}`);
