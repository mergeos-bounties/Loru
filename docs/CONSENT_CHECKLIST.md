# Consent Checklist for Real-Video Sign Packs

## Overview

This document outlines the consent, face blur, and attribution requirements when using real sign language video in Loru sign packs.

## Consent Requirements

### Before Recording

- [ ] **Written consent** obtained from all participants
- [ ] **Parental consent** for participants under 18
- [ ] **Purpose explained** clearly (educational/app usage)
- [ ] **Usage rights** specified (non-commercial, commercial, etc.)
- [ ] **Withdrawal rights** explained (can revoke consent anytime)
- [ ] **Contact information** provided for questions

### Consent Form Must Include

1. **Participant Information**
   - Full name
   - Age (or parental signature if under 18)
   - Contact information

2. **Project Details**
   - Project name (Loru Sign Language Dictionary)
   - Organization name
   - Purpose of recording
   - How video will be used

3. **Rights Granted**
   - Usage in educational materials
   - Usage in app/software
   - Attribution requirements
   - Duration of usage rights

4. **Restrictions**
   - Commercial use restrictions
   - Modification restrictions
   - Distribution restrictions

5. **Signature**
   - Participant signature
   - Date
   - Witness signature (if required)

## Face Blur Requirements

### When to Apply Face Blur

- [ ] **Public figures** - Always blur unless explicit permission
- [ ] **Minors** - Always blur unless parental consent includes face display
- [ ] **Privacy concerns** - Blur if participant requests
- [ ] **Background faces** - Blur all non-participant faces

### How to Apply Face Blur

1. **Detect faces** using OpenCV or similar
2. **Apply Gaussian blur** (kernel size 51-101)
3. **Ensure consistency** - same blur level throughout video
4. **Verify coverage** - all faces properly blurred
5. **Test playback** - ensure blur is effective

### Quality Standards

- **Minimum blur radius**: 30 pixels
- **Consistency**: Same blur level throughout
- **Coverage**: 100% of identified faces
- **Performance**: No lag or stuttering

## Attribution Requirements

### Required Attribution

When using real video, include:

```
Video provided by [Participant Name]
Used with permission for Loru Sign Language Dictionary
© [Year] [Organization Name]
```

### Attribution Placement

- **In-app**: Credits screen or settings
- **Documentation**: README or about page
- **Marketing materials**: If used in promotions
- **Open source**: If code is distributed

### Attribution Format

```markdown
## Video Credits

- [Participant Name] - [Sign Language] - [Date]
- Used with written consent for educational purposes
- © 2026 Loru Project
```

## Documentation Requirements

### Files to Maintain

1. **consent_forms/** - Original signed consent forms
2. **release_forms/** - Any release forms
3. **attribution.md** - Credits for all participants
4. **usage_log.md** - How each video is used

### Record Keeping

- **Retention period**: 5 years minimum
- **Access**: Only authorized team members
- **Backup**: Secure cloud storage
- **Encryption**: Sensitive data encrypted at rest

## Quality Checklist

### Pre-Release

- [ ] All consent forms collected and signed
- [ ] Face blur applied where required
- [ ] Attribution text prepared
- [ ] Usage rights verified
- [ ] Privacy policy updated
- [ ] Legal review completed (if needed)

### Post-Release

- [ ] Attribution displayed correctly
- [ ] Face blur verified in production
- [ ] Consent forms archived
- [ ] Usage log updated
- [ ] Participant feedback collected

## Legal Considerations

### Jurisdiction

- **GDPR** (EU): Additional requirements for EU participants
- **CCPA** (California): Specific rights for California residents
- **Local laws**: Check local privacy regulations

### Age Requirements

- **Under 13**: Parental consent required (COPPA)
- **Under 18**: Parental consent recommended
- **18+**: Individual consent sufficient

### Commercial Use

- **Non-commercial**: Standard consent sufficient
- **Commercial**: Additional licensing agreement required
- **Open source**: Verify compatibility with license

## Templates

### Consent Form Template

```
CONSENT FORM

I, [PARTICIPANT_NAME], hereby consent to participate in the 
Loru Sign Language Dictionary project.

I understand that:
1. My video will be used for educational purposes
2. My face may be visible in the final product
3. I can withdraw consent at any time
4. My personal information will be kept confidential

I grant permission for:
- [ ] Non-commercial use
- [ ] Commercial use
- [ ] Modification
- [ ] Distribution

Signature: _______________________
Date: _______________________
Witness: _______________________
```

### Attribution Template

```
VIDEO CREDITS

Sign Language: [LANGUAGE]
Performer: [NAME]
Date Recorded: [DATE]
Consent Verified: [DATE]
Usage: [PURPOSE]

© 2026 Loru Project. Used with permission.
```

## References

- [GDPR Guidelines](https://gdpr.eu/)
- [CCPA Information](https://oag.ca.gov/privacy/ccpa)
- [COPPA Rules](https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa)
- [Creative Commons](https://creativecommons.org/)
