# Loru

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.3.0-0E8A16.svg)](pyproject.toml)
[![Qt GUI](https://img.shields.io/badge/GUI-PySide6-41CD52.svg)](src/loru/gui/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MergeOS](https://img.shields.io/badge/MergeOS-bounties-5319E7.svg)](https://github.com/mergeos-bounties)

**Loru** is an offline **sign language** toolkit: landmark sequences → gloss/text, and sign → **voice (WAV)** — demos and train loops without a GPU for the smoke path.

**Product:** [mergeos-bounties/Loru](https://github.com/mergeos-bounties/Loru)

---

## Table of contents

- [Highlights](#highlights)
- [Desktop GUI (Qt)](#desktop-gui-qt)
- [Screenshots](#screenshots)
- [Quick start](#quick-start)
- [CLI reference](#cli-reference)
- [Data & pipeline](#data--pipeline)
- [Diagrams](#diagrams)
- [Repository layout](#repository-layout)
- [Development](#development)
- [MergeOS bounties](#mergeos-bounties)
- [License](#license)

---

## Highlights

| Mode | Description |
| --- | --- |
| **Sign → text** | Landmark JSON sequences → gloss / sentence |
| **Sign → voice** | Recognition + TTS-style WAV export |
| **Offline demo** | Samples, toy train, infer `hello` end-to-end |
| **Desktop GUI** | Modern **PySide6** app (`loru-gui`) |
| **Gloss vocab** | Default gloss set for demos |
| **Serve** | Optional FastAPI for integrations |

---

## Desktop GUI (Qt)

Modern dark **PySide6** demo shell — full demo, samples, infer, train, gloss vocab.