# Presentation source — version 3.1, 15 November 2026

`content.json` holds the confirmed roster, concrete design contributions, speaker
notes, timing and verified references. `scripts/build_presentation.py` generates
an editable 12-slide PowerPoint, script, viva preparation, rubric checklist and
contribution ledger into an explicit directory outside the repository. The
optional Python presentation extra installs python-pptx; LibreOffice exports PDF.

```bash
.venv/bin/python -m pip install -e '.[presentation]'
.venv/bin/python scripts/build_presentation.py --output /tmp/renalguard-presentation
libreoffice --headless --convert-to pdf --outdir /tmp/renalguard-presentation /tmp/renalguard-presentation/RENAL_GUARD_Final_Midterm_Presentation.pptx
```

Older local decks were preserved. The new cards attribute the user's explicitly
supplied proposal/design contributions, not fabricated completed experiments.
Personal institutional details remain unverified. Presentation quality and timing
checks are recorded in the rubric and release verification. Do not claim a
rehearsal or supervisor approval that has not occurred.
