# Sign Language Datasets — Public Catalog

> **Audience:** Loru contributors picking a public sign-language corpus for training,
> validation, or demo data.
>
> **Rule:** this catalog documents only — it never bundles or redistributes any
> media. Always re-fetch from the official source. License-respect-first.

Each row lists: dataset, modality, language, approximate size, license (SPDX),
official URL + canonical citation, and a safe-to-use note.

## Catalog

### 1. WLASL (Word-Level American Sign Language)
- **Modality:** video (cropped short clips)
- **Language:** ASL (American Sign Language)
- **Size:** ~21,083 instances across 2,000+ glosses
- **License:** Mixed — see official site; many clips fall under fair use for research, redistribution restricted
- **URL:** https://github.com/dxli94/WLASL
- **Citation:** Li, D. et al. (2020). *Word-level Deep Sign Language Recognition from Video.* ECCV.
- **Safe-to-use notes:** Use for training/eval. Do NOT mirror the video corpus publicly. Cite the paper in any downstream work.

### 2. MS-ASL (Microsoft American Sign Language)
- **Modality:** video (TV/news clips with signer overlays)
- **Language:** ASL
- **Size:** ~25,513 instances, 1,000 signs, 222 signers
- **License:** Research-only; redistribution of source clips prohibited
- **URL:** https://www.microsoft.com/en-us/research/project/ms-asl/
- **Citation:** Joze, H. R. V., & Koller, O. (2018). *MS-ASL: A Large-Scale Data Set and Benchmark for Understanding American Sign Language.* CVPR Workshop.
- **Safe-to-use notes:** Apply for download from Microsoft Research. Cite the dataset version you used.

### 3. How2Sign
- **Modality:** video (multi-modal: RGB + depth + 2D/3D skeleton)
- **Language:** ASL
- **Size:** ~80 hours of video, 16K vocabulary, ~35K video clips
- **License:** CC-BY-NC-SA 4.0 for non-commercial research
- **URL:** https://how2sign.github.io/
- **Citation:** Duarte, A. et al. (2021). *How2Sign: A Large-scale Multimodal Dataset for Continuous American Sign Language.* CVPR.
- **Safe-to-use notes:** Allowed for non-commercial research with attribution. No commercial use without explicit license negotiation.

### 4. Phoenix-2014T (Continuous Sign Language Recognition)
- **Modality:** video (German weather broadcast, signer inset)
- **Language:** DGS (German Sign Language)
- **Size:** ~8257 training / 642 development / 987 test sentences
- **License:** Research-only; redistribution restricted
- **URL:** https://www-i6.informatik.rwth-aachen.de/~koller/RWTH-PHOENIX-2014-T/
- **Citation:** Forster, J. et al. (2014). *Extensions of the Sign Language Recognition and Translation Corpus RWTH-PHOENIX-Weather.* LREC.
- **Safe-to-use notes:** Apply for access. Cite the corpus version. For non-German sign languages, look at the more recent Phoenix-2014T release notes.

### 5. BSL-1K (British Sign Language)
- **Modality:** video (BBC broadcasts)
- **Language:** BSL (British Sign Language)
- **Size:** ~1,000 hours, ~40K sign instances, 40 signers
- **License:** Research-only; redistribution restricted
- **URL:** https://www.kaggle.com/datasets/ayuraj/bsl-1k
- **Citation:** Albanie, S. et al. (2020). *BSL-1K: Scaling Up Co-Articulated Sign Language Recognition Using a Million-Word BSL Corpus.* CVPR.
- **Safe-to-use notes:** Available via Kaggle. Cite the dataset card version. Respects BBC broadcast rights.

### 6. Jester (Gesture Recognition)
- **Modality:** video (webcam, single-hand gestures)
- **Language:** N/A (gesture set, not sign language)
- **Size:** ~148,092 frames, 27 gesture classes, 1,378 subjects
- **License:** CC-BY 4.0 (research-friendly, allows redistribution with attribution)
- **URL:** https://20bn.com/datasets/jester
- **Citation:** Materzynska, J. et al. (2019). *The Jester Dataset: A Large-Scale Video Dataset of Daily Gestures.* ICCV Workshop.
- **Safe-to-use notes:** Best for **gesture** recognition (not sign language). Useful for negative-class training and smoke tests. Redistributable under CC-BY with attribution.

### 7. Sign Language MNIST
- **Modality:** static images (28x28 grayscale hand signs)
- **Language:** ASL (letters A-Y, no J)
- **Size:** ~34,627 training + 7,172 test images, 24 classes
- **License:** MIT (very permissive)
- **URL:** https://www.kaggle.com/datasets/datamunge/sign-language-mnist
- **Citation:** Sign-MNIST is a derivative of the MNIST format applied to ASL letters; originally popularized on Kaggle.
- **Safe-to-use notes:** Excellent for smoke tests and quick demos. Static images only — not useful for sequence/temporal models. Safe to redistribute.

### 8. INCLUDE (Indian Sign Language)
- **Modality:** video (multi-signer, complex scenes)
- **Language:** ISL (Indian Sign Language)
- **Size:** ~4287 video clips, 263 signs, 75 signers
- **License:** Research-only; redistribution restricted
- **URL:** https://github.com/senarvithe/include
- **Citation:** Sridhar, A. et al. (2020). *INCLUDE: A Large Scale Dataset for Indian Sign Language Recognition.* ACM MM.
- **Safe-to-use notes:** Use for ISL research. Cite the paper. Do not redistribute videos.

### 9. VSLT-LSFB (Belgian French Sign Language)
- **Modality:** video (lectures, news, public broadcast)
- **Language:** LSFB (Belgian French Sign Language)
- **Size:** ~100+ hours, continuous signing, sentence-level annotations
- **License:** CC-BY-NC-ND 4.0 (research + non-commercial, no derivatives)
- **URL:** https://sign-lfb.ulb.ac.be/
- **Citation:** Camgöz, N. C. et al. (2020). *LSFB-CONT and LSFB-ISO: Two New Datasets for Vision-Based Sign Language Recognition and Translation.* LREC.
- **Safe-to-use notes:** Allowed for non-commercial research. No derivative works without license negotiation. Cite the dataset card.

### 10. AUTSL (Ankara University Turkish Sign Language)
- **Modality:** video (multi-angle, depth sensor)
- **Language:** TSL (Turkish Sign Language)
- **Size:** ~38,336 instances, 226 signs, 43 signers
- **License:** Research-only; redistribution restricted
- **URL:** https://cvml.ankara.edu.tr/datasets/
- **Citation:** Sincan, S. O., & Keles, H. Y. (2020). *AUTSL: A Large Scale Multi-Modal Turkish Sign Language Dataset and Baseline Methods.* IEEE Access.
- **Safe-to-use notes:** Apply for access. Useful for low-resource sign language research.

## How to pick

| Use case | Best fit |
| --- | --- |
| Sequence/temporal model training | How2Sign, WLASL, MS-ASL, Phoenix-2014T, BSL-1K, AUTSL |
| Static-gesture smoke test | Sign Language MNIST, Jester |
| Gesture (not sign language) baseline | Jester |
| Multi-language coverage | WLASL + How2Sign (ASL) + Phoenix-2014T (DGS) + BSL-1K (BSL) + INCLUDE (ISL) + AUTSL (TSL) + VSLT-LSFB (LSFB) |
| Permissive license for redistribution | Sign Language MNIST (MIT), Jester (CC-BY 4.0) |
| Industrial / commercial use | None in this catalog — most require explicit license negotiation |

## Ethics note (matches Loru README)

These corpora document communities that include deaf and hard-of-hearing
contributors. Always:
- Cite the dataset and the original researchers
- Disclose how your downstream work uses the data
- Avoid using sign-language corpora for surveillance, biometric profiling,
  or any use that the contributing community would object to
- Prefer corpora that the contributing community helped build and approved

## Citation pattern

If you build on multiple datasets, cite each. For Loru downstream work, also
cite this catalog:

```bibtex
@misc{loru-datasets-catalog,
  title = {Sign Language Datasets Catalog (Loru)},
  author = {{Loru contributors}},
  year = {2026},
  howpublished = {\url{https://github.com/mergeos-bounties/Loru/blob/master/docs/DATASETS.md}}
}
```