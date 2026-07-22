# Loru — Accessibility Guide

Loru is an offline sign language toolkit. This document describes who the tool is designed for, its current limitations, consent obligations, and when human interpreters remain essential.

## Intended Users

Loru is designed for:

- **Developers and researchers** building or evaluating sign language recognition pipelines
- **Accessibility tool integrators** looking for an offline, open-source sign-to-text and sign-to-voice foundation
- **Sign language learners** exploring isolated gloss recognition in a controlled, non-production setting
- **Educational technology projects** demonstrating sign language concepts with synthetic or consent-cleared data

Loru is **not** a certified medical or accessibility device and must not be relied upon for critical communication.

## Limitations of Automated Sign Language Recognition

Automated sign language recognition (SLR), including Loru's models, has inherent limitations:

### Vocabulary and Coverage
- Loru ships with a small gloss vocabulary for demos and toy training. Real-world sign languages have thousands of signs with regional, cultural, and personal variation.
- The toolkit does not support continuous/fluent signing recognition out of the box.

### Landmark Fidelity
- Loru relies on MediaPipe-style landmark keypoints. Poor lighting, occluded hands, fast motion, or low-resolution input degrade recognition quality.
- Facial expressions, mouthing, and non-manual markers — critical to meaning in sign languages — are not fully captured.

### Model Scope
- The toy training pipeline demonstrates feasibility, not production accuracy.
- No model shipped with Loru has been clinically or professionally validated for communication, interpretation, or translation.

### Cultural and Linguistic Nuance
- Sign languages are full natural languages with distinct grammar, idioms, and cultural context. Loru operates at the gloss/surface level and does not model syntactic or pragmatic structure.
- Dialectal variation between regions, age groups, and Deaf communities is not accounted for.

## Consent

Any real sign language video included in Loru datasets, sign packs, or training pipelines must follow the project's consent requirements:

1. **Written consent** from every participant before recording
2. **Parental or guardian consent** for participants under 18
3. **Clear explanation** of how recordings will be used (training, demo, distribution)
4. **Right to withdraw** — participants may revoke consent and request removal at any time
5. **Face blur** applied per the consent checklist where required

See [CONSENT_CHECKLIST.md](CONSENT_CHECKLIST.md) and [CONSENT_TEMPLATE.md](CONSENT_TEMPLATE.md) for full procedures and templates.

## When Human Interpreters Are Required

Loru **must not** replace a qualified human interpreter in any of the following situations:

| Context | Why a Human Is Required |
|---|---|
| **Medical settings** | Misinterpretation can cause serious harm. Certified medical interpreters understand clinical terminology and patient confidentiality. |
| **Legal proceedings** | Court rulings, contracts, depositions, and police interactions require certified court interpreters. |
| **Emergency services** | 911 calls, disaster response, and hospital triage demand reliable real-time interpretation. |
| **Mental health counselling** | Therapeutic nuance requires professional interpreters trained in mental health contexts. |
| **Educational assessments** | IEP meetings, academic evaluations, and placement decisions need qualified interpreter support. |
| **Financial and legal documents** | Mortgages, visas, immigration, and insurance forms require certified review. |

### General Principle

Any setting where misunderstanding could lead to legal, financial, medical, or emotional harm requires a qualified human interpreter. Loru is an offline research and demonstration toolkit — it is not a substitute for professional sign language interpretation.

## Safety Language

- Loru does **not** claim to provide communication access or to replace assistive technologies prescribed by healthcare professionals.
- The project makes **no warranty**, express or implied, about the accuracy, reliability, or completeness of any recognition or voice output.
- Developers integrating Loru into their own applications are responsible for conducting appropriate risk assessments, usability testing with Deaf and hard-of-hearing users, and compliance with applicable accessibility laws and regulations.

## References

- [CONSENT_CHECKLIST.md](CONSENT_CHECKLIST.md)
- [CONSENT_TEMPLATE.md](CONSENT_TEMPLATE.md)
- [World Federation of the Deaf](https://wfdeaf.org/)
- [RIT / National Technical Institute for the Deaf](https://www.rit.edu/ntid/)
- [W3C Accessibility Guidelines](https://www.w3.org/TR/WCAG22/)
