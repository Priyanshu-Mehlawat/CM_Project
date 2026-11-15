"""Generate the editable team deck from reviewed public source content.

Requires optional python-pptx. Output belongs outside the repository; slides do
not contain patient records or fabricated model results.
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT):
        parser.error("Keep generated presentation binaries outside the source repository")
    output.mkdir(parents=True, exist_ok=True)
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.util import Inches, Pt

    data = json.loads((ROOT / "docs/presentation/content.json").read_text())
    deck = Presentation()
    deck.slide_width, deck.slide_height = Inches(13.333), Inches(7.5)
    navy, teal, muted, pale = "102C3D", "087F82", "536B79", "EFF6F7"

    def box(slide, x, y, width, height, color=pale):
        item = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(width), Inches(height)
        )
        item.fill.solid()
        item.fill.fore_color.rgb = RGBColor.from_string(color)
        item.line.fill.background()
        item.adjustments[0] = 0.12

    def text(slide, value, x, y, width, height, size=18, color=navy, bold=False):
        frame = slide.shapes.add_textbox(
            Inches(x), Inches(y), Inches(width), Inches(height)
        ).text_frame
        frame.word_wrap = True
        frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
        for index, line in enumerate(value.split("\n")):
            p = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
            p.text = line
            p.font.name, p.font.size, p.font.bold = "Aptos", Pt(size), bold
            p.font.color.rgb = RGBColor.from_string(color)
            p.space_after = Pt(3)

    def slide(title, category, number):
        s = deck.slides.add_slide(deck.slide_layouts[6])
        box(s, 0, 0, 0.13, 7.5, teal)
        text(s, category.upper(), 0.62, 0.35, 12, 0.25, 11, teal, True)
        text(s, title, 0.62, 0.83, 12, 0.68, 28, navy, True)
        box(s, 0.65, 7.05, 12, 0.012, "D6E5E8")
        text(
            s,
            "RENAL-GUARD · RESEARCH PROTOTYPE · TEAM-CONFIRMED DESIGN CONTRIBUTIONS",
            0.67,
            7.18,
            10.8,
            0.2,
            8,
            muted,
        )
        text(
            s,
            f"{number:02d} / {'07' if number <= 7 else 'BACKUP'}",
            11.55,
            7.16,
            1.1,
            0.22,
            9,
            teal,
            True,
        )
        if number <= 7:
            s.notes_slide.notes_text_frame.text = data["notes"][number - 1]
        return s

    def banner(s, value, y=6.3):
        box(s, 0.7, y, 11.95, 0.5, navy)
        text(s, value, 0.93, y + 0.12, 11.5, 0.3, 14, "FFFFFF", True)

    def card(s, x, y, width, height, title, body):
        box(s, x, y, width, height)
        text(s, title, x + 0.22, y + 0.22, width - 0.44, 0.7, 21, navy, True)
        text(
            s,
            body,
            x + 0.22,
            y + (0.88 if height < 2 else 1.2),
            width - 0.44,
            height - (0.98 if height < 2 else 1.35),
            14 if height < 2 else 16,
            muted,
        )

    s = slide("RENAL-GUARD", "Research vision · mid-term evaluation", 1)
    text(
        s,
        (
            "Early Prediction of Acute Kidney Injury Progression\nin ICU Patients "
            "Using Machine Learning"
        ),
        0.7,
        1.65,
        11.8,
        1.2,
        27,
        navy,
        True,
    )
    box(s, 0.7, 3.05, 11.9, 1.05, navy)
    text(
        s,
        "Predicting deterioration before acute kidney injury progresses.",
        0.98,
        3.3,
        11.2,
        0.65,
        25,
        "FFFFFF",
        True,
    )
    for index, (name, roll, _, _) in enumerate(data["team"]):
        text(s, f"{name} · {roll}", 0.72 + index % 3 * 4.02, 4.7 + index // 3 * 0.44, 3.9, 0.35, 13)
    text(
        s,
        "Group 31 · [Course / institution / supervisor: confirm]",
        0.73,
        6.37,
        11.7,
        0.35,
        13,
        muted,
    )

    s = slide("Progression is a specific forecasting problem", "Background · 10 marks", 2)
    box(s, 0.7, 1.7, 3, 3.65, navy)
    text(s, "57.3%", 0.98, 2.06, 2.45, 0.85, 43, "FFFFFF", True)
    text(
        s,
        "AKI in week one\n1,802 ICU patients\nAKI-EPI · full KDIGO [1]",
        0.98,
        3.3,
        2.45,
        1.3,
        17,
        "FFFFFF",
    )
    text(
        s,
        (
            "AKI is an acute decline in kidney function.\nKDIGO uses creatinine an"
            "d/or urine output. [2]"
        ),
        4.08,
        1.77,
        8.3,
        1,
        20,
    )
    for index, (a, b) in enumerate(
        [
            ("Stage 1", "First eligible assessment"),
            ("Prediction", "Information known now"),
            ("Stage 2/3?", "Subsequent 48 hours"),
        ]
    ):
        x = 4.08 + index * 2.86
        box(s, x, 3.12, 2.6, 1.15)
        text(s, a, x + 0.16, 3.33, 2.3, 0.36, 19, teal, True)
        text(s, b, x + 0.16, 3.88, 2.3, 0.3, 12, muted)
    text(
        s,
        (
            "Prior progression models exist. [5]\nOur focus: availability-aware St"
            "age 1 → Stage 2/3\nwith a comparable independent external cohort."
        ),
        4.08,
        4.73,
        8.3,
        1.08,
        19,
        navy,
        True,
    )
    banner(s, "Potential value: earlier risk assessment; clinical benefit remains untested.")

    s = slide("Falsifiable hypotheses and a strict time cutoff", "Hypothesis · 10 marks", 3)
    box(s, 0.7, 1.7, 11.9, 1.08, navy)
    text(
        s,
        (
            "H1  Known Stage 1 information contains predictive signal\nfor Stage 2"
            "/3 progression within the next 48 hours."
        ),
        0.97,
        1.9,
        11.3,
        0.8,
        23,
        "FFFFFF",
        True,
    )
    text(
        s,
        "H2  Nonlinear models may improve over Logistic Regression.",
        0.76,
        3.1,
        11.8,
        0.6,
        21,
        teal,
        True,
    )
    box(s, 0.8, 4.2, 4.6, 0.9)
    text(s, "PRE-INDEX\nAvailable observations only", 1, 4.36, 4.1, 0.65, 17, teal, True)
    text(s, "t₀", 5.43, 3.85, 0.6, 0.4, 23, teal, True)
    box(s, 5.6, 4.12, 0.04, 1.2, teal)
    box(s, 5.94, 4.2, 6.6, 0.9, navy)
    text(s, "OUTCOME ONLY\n(t₀, t₀ + 48 hours]", 6.2, 4.36, 6.1, 0.65, 17, "FFFFFF", True)
    banner(s, "AUROC · AUPRC + prevalence · calibration · Brier score · no assumed winner")

    s = slide("Dataset and cohort engineering", "Dataset · 10 marks", 4)
    card(
        s,
        0.7,
        1.7,
        5.8,
        2.6,
        "MIMIC-IV · development",
        (
            "Single-center hospital/ICU resource [3]\nDemographics, labs and physi"
            "ology\nProject access/cohort: not yet confirmed"
        ),
    )
    card(
        s,
        6.84,
        1.7,
        5.8,
        2.6,
        "eICU-CRD · external test",
        (
            "Multihospital ICU resource [4]\nShared concepts and credible timestam"
            "ps\nExternal use requires comparable labels"
        ),
    )
    text(
        s,
        "Adult ICU → Eligible Stage 1 → Available features → 48-hour outcome",
        0.8,
        4.76,
        11.8,
        0.65,
        21,
        teal,
        True,
    )
    text(
        s,
        (
            "Audit before labeling: baseline creatinine · timing · adequate follo"
            "w-up\nDataset documentation analysis is complete; patient extraction "
            "is not claimed."
        ),
        0.8,
        5.62,
        11.8,
        0.85,
        17,
        muted,
    )

    s = slide("A repaired workbench with explicit research gates", "Feasibility · 10 marks", 5)
    stages = [
        "Audit",
        "Cohort",
        "Time-safe\nfeatures",
        "48h labels",
        "LR / XGB",
        "Internal\nevaluation",
        "External\nif feasible",
    ]
    for index, a in enumerate(stages):
        x = 0.7 + index * 1.73
        box(s, x, 1.76, 1.52, 0.99)
        text(s, a, x + 0.12, 1.96, 1.28, 0.64, 14, teal, True)
    text(
        s,
        (
            "Patient grouping · training-only preprocessing · missingness audit\nP"
            "respecified model comparison · discrimination + calibration · frozen"
            " external test"
        ),
        0.8,
        3.13,
        11.7,
        0.86,
        18,
    )
    card(
        s,
        0.7,
        4.27,
        5.8,
        1.73,
        "Implemented & verified",
        "Synthetic API/replay · correction tests · real browser workflow",
    )
    card(
        s,
        6.84,
        4.27,
        5.8,
        1.73,
        "Research still conditional",
        "Access · baseline/follow-up policy · real training and validation",
    )
    banner(
        s,
        "Risks → isolated audit, explicit unknowns, baseline-first plan and honest evidence",
        6.45,
    )

    s = slide(
        "Individual contribution — specific and fairly represented",
        "Team-confirmed proposal/design deliverables · equal prominence",
        6,
    )
    for index, (name, roll, role, deliverable) in enumerate(data["team"]):
        x = 0.7 + index % 3 * 4.15
        y = 1.7 + index // 3 * 1.58
        box(s, x, y, 3.94, 1.43)
        text(s, name, x + 0.17, y + 0.12, 3.60, 0.3, 16, navy, True)
        text(s, roll, x + 0.17, y + 0.47, 3.60, 0.21, 10, teal, True)
        text(s, role, x + 0.17, y + 0.78, 3.60, 0.29, 13, navy, True)
        text(s, deliverable, x + 0.17, y + 1.12, 3.60, 0.25, 10, muted)
    text(
        s,
        (
            "Attribution: team statement, 15 Nov 2026. Design contributions ≠ com"
            "pleted experiments. See evidence ledger."
        ),
        0.76,
        6.65,
        11.8,
        0.27,
        12,
        teal,
    )

    s = slide("Expected research outcomes", "Conclusion · research value", 7)
    for index, (a, b) in enumerate(
        [
            ("Reproducible labels", "An auditable cohort and three-state progression outcome"),
            ("Fair model comparison", "Interpretable and nonlinear methods, honestly evaluated"),
            ("Generalization", "Independent external evaluation if data are comparable"),
        ]
    ):
        card(s, 0.7 + index * 4.15, 1.85, 3.93, 2.7, a, b)
    box(s, 0.75, 5.15, 11.85, 1.06, navy)
    text(
        s,
        "From detecting kidney injury\nto anticipating its progression.",
        1.03,
        5.28,
        11.3,
        0.9,
        23,
        "FFFFFF",
        True,
    )
    text(
        s,
        (
            "An integrated synthetic prototype is evidence of software progress, "
            "not clinical validation."
        ),
        0.8,
        6.55,
        11.8,
        0.3,
        14,
        muted,
    )

    s = slide("Verified scientific references", "Backup · outside five-minute delivery", 8)
    for index, (citation, url) in enumerate(data["references"]):
        y = 1.75 + index * 0.98
        text(s, f"[{index + 1}] {citation}", 0.8, y, 11.6, 0.4, 15, navy, True)
        text(s, url, 0.8, y + 0.43, 11.6, 0.37, 11, teal)
    text(
        s,
        (
            "AKI-EPI used full KDIGO; its rate is not our progression prevalence."
            "\nWei et al. studied Stage 1/2 → Stage 3; the proposed target here di"
            "ffers."
        ),
        0.8,
        6.66,
        11.7,
        0.35,
        10,
        muted,
    )

    backups = [
        (
            "Operational staging and outcomes",
            [
                ("AKI first", "≥0.3 mg/dL within 48h or ≥1.5× eligible baseline within 7 days."),
                (
                    "Creatinine stage",
                    (
                        "Stage 1: 1.5–1.9× or qualifying absolute rise; Stage 2: 2–2.9×; Stag"
                        "e 3: ≥3× or ≥4.0 mg/dL with AKI established."
                    ),
                ),
                (
                    "Index / outcome",
                    (
                        "First eligible confirmed Stage 1; outcome strictly after index throu"
                        "gh +48h. Adequately observed negative differs from unknown."
                    ),
                ),
                (
                    "Limits",
                    (
                        "Fixture reference/ascertainment are explicit synthetic assertions. N"
                        "o research baseline or follow-up default has been invented."
                    ),
                ),
            ],
        ),
        (
            "Leakage and validation defense",
            [
                (
                    "Availability",
                    (
                        "Collection and publication differ; only results known by index enter"
                        " predictors. Corrected samples replace older versions as available."
                    ),
                ),
                (
                    "Splits",
                    (
                        "Group by patient. Fit preprocessing, model selection, calibration an"
                        "d thresholds on permitted development partitions only."
                    ),
                ),
                (
                    "Metrics",
                    (
                        "Report AUROC, AUPRC with prevalence, Brier/calibration, counts, unkn"
                        "owns and defensible patient-level uncertainty."
                    ),
                ),
                (
                    "External test",
                    (
                        "Freeze pipeline before a comparable eICU test. Previously inspected "
                        "audits are not fresh independent validation."
                    ),
                ),
            ],
        ),
        (
            "Software evidence and unfinished science",
            [
                (
                    "Implemented",
                    (
                        "One API contract; generated types and runtime schemas; synthetic epi"
                        "sode replay; correction-aware creatinine engine."
                    ),
                ),
                (
                    "Verified",
                    (
                        "Python, React and real desktop/mobile browser checks; drift, privacy"
                        " and localhost proxy checks. See release verification log."
                    ),
                ),
                (
                    "Unfinished",
                    (
                        "Authorized cohort extraction, clinical policy approval, trained prog"
                        "ression model and independent internal/external evaluation."
                    ),
                ),
                (
                    "Data boundary",
                    (
                        "No upstream onset model, patient export, seeded auth layer or extern"
                        "al AI summary is imported into this release."
                    ),
                ),
            ],
        ),
    ]
    for number, (title, rows) in enumerate(backups, 9):
        s = slide(title, "Technical defense · backup", number)
        for index, (a, b) in enumerate(rows):
            y = 1.74 + index * 1.23
            box(s, 0.75, y, 11.85, 1.07)
            text(s, a, 0.98, y + 0.17, 2.0, 0.68, 17, teal, True)
            text(s, b, 3.22, y + 0.17, 9.12, 0.78, 15)
    s = slide(
        "Contribution evidence and assessment questions",
        "Backup · team-confirmed design attribution",
        12,
    )
    for index, (name, _, role, _) in enumerate(data["team"]):
        y = 1.72 + index * 0.52
        text(s, name, 0.8, y, 3.2, 0.3, 14, navy, True)
        text(s, role, 4.1, y, 5.4, 0.3, 14, teal)
        text(s, "Team-confirmed design", 9.6, y, 2.8, 0.3, 12, muted)
    text(
        s,
        (
            "Full ledger maps each deliverable to project material and an oral-de"
            "fense question.\nIt does not infer sole code authorship or credit exp"
            "eriments that have not occurred."
        ),
        0.8,
        6.52,
        11.6,
        0.5,
        13,
        muted,
    )

    deck.save(output / "RENAL_GUARD_Final_Midterm_Presentation.pptx")
    for name in ("RENAL_GUARD_Viva_Preparation.md", "RENAL_GUARD_Rubric_Checklist.md"):
        (output / name).write_text((ROOT / "docs/presentation" / name).read_text())
    (output / "RENAL_GUARD_Contribution_Ledger.md").write_text(
        (ROOT / "docs/team_contributions.md").read_text()
    )
    script = (
        "# RENAL-GUARD — five-minute team script\n\nVersion 3.1 · Generated "
        + data["generated"]
        + ". Target 4:50 with 10 seconds buffer.\n\n"
        "Speaker names are cues, not spoken words. Team-confirmed contributions are "
        "proposal/design work, not completed experiments. Timing requires rehearsal.\n\n"
    )
    for index, (note, seconds) in enumerate(zip(data["notes"], data["timings"]), 1):
        script += f"## Slide {index} — {seconds} seconds\n\n{note}\n\n"
    script += (
        "## Rehearsal\n\nAll nine members have a substantive explanation tied to their "
        "confirmed workstream. Do not narrate backup slides. Priyanshu Mehlawat introduces "
        "the question and hypothesis; Harshit covers evidence; Shaurya features/leakage; "
        "Shourya datasets; Rishi cohort/outcomes; Priyanshu the API; Hemendra model choice; "
        "Ayan validation/conclusion; Tejas interaction design and contribution evidence. "
        "Institution, exact course title and supervisor remain to be confirmed.\n"
    )
    (output / "RENAL_GUARD_5_Minute_Team_Script.md").write_text(script)
    print(f"Generated {len(deck.slides)} slides and team script in {output}")


if __name__ == "__main__":
    main()
