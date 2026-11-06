#!/usr/bin/env python3
"""Build a PDF resume from the shared JSON source of truth."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def load_resume(resume_path: Path) -> dict:
    with resume_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def register_fonts() -> tuple[str, str]:
    font_candidates = [
        (
            "ResumeBody",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        ),
        (
            "ResumeBody",
            "/Library/Fonts/Arial.ttf",
            "/Library/Fonts/Arial Bold.ttf",
        ),
    ]

    for font_name, regular_path, bold_path in font_candidates:
        regular_file = Path(regular_path)
        bold_file = Path(bold_path)
        if regular_file.exists() and bold_file.exists():
            pdfmetrics.registerFont(TTFont(font_name, str(regular_file)))
            pdfmetrics.registerFont(TTFont(f"{font_name}-Bold", str(bold_file)))
            return font_name, f"{font_name}-Bold"

    return "Helvetica", "Helvetica-Bold"


def paragraph_styles(body_font: str, bold_font: str):
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ResumeName",
            parent=styles["Title"],
            fontName=bold_font,
            fontSize=23,
            leading=27,
            textColor=colors.HexColor("#2A2438"),
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ResumeBody",
            parent=styles["BodyText"],
            fontName=body_font,
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#241F2E"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="ResumeBodyRight",
            parent=styles["BodyText"],
            fontName=body_font,
            fontSize=9.5,
            leading=13,
            alignment=TA_RIGHT,
            textColor=colors.HexColor("#241F2E"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="ResumeSection",
            parent=styles["Heading2"],
            fontName=bold_font,
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#65558F"),
            spaceBefore=8,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ResumeRole",
            parent=styles["BodyText"],
            fontName=bold_font,
            fontSize=10.5,
            leading=13,
            textColor=colors.HexColor("#241F2E"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="ResumeMeta",
            parent=styles["BodyText"],
            fontName=body_font,
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#65558F"),
        )
    )
    return styles


def bullet_flowable(items: list[str], style, body_font: str):
    return ListFlowable(
        [ListItem(Paragraph(item, style), leftIndent=0) for item in items],
        bulletType="bullet",
        bulletFontName=body_font,
        bulletFontSize=8,
        leftIndent=13,
        bulletOffsetY=2,
    )


def section_heading(title: str, styles) -> Paragraph:
    return Paragraph(title, styles["ResumeSection"])


def build_story(resume: dict, styles, body_font: str) -> list:
    story = []

    left = [
        Paragraph(resume["basics"]["name"], styles["ResumeName"]),
        Paragraph(resume["basics"]["location"], styles["ResumeMeta"]),
        Paragraph(resume["summary"], styles["ResumeBody"]),
    ]
    right = [
        Paragraph(resume["basics"]["email"], styles["ResumeBodyRight"]),
        Paragraph(resume["basics"]["linkedin"], styles["ResumeBodyRight"]),
        Paragraph(resume["basics"]["github"], styles["ResumeBodyRight"]),
    ]

    header_table = Table(
        [[left, right]],
        colWidths=[4.6 * inch, 2.5 * inch],
        style=TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        ),
    )
    story.append(header_table)
    story.append(Spacer(1, 0.12 * inch))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#B2AAC7"), thickness=1))
    story.append(Spacer(1, 0.12 * inch))

    story.append(section_heading("skills", styles))
    skill_table_data = []
    for skill_group in resume["skills"]:
        skill_table_data.append(
            [
                Paragraph(f"<b>{skill_group['category']}</b>", styles["ResumeBody"]),
                Paragraph(", ".join(skill_group["items"]), styles["ResumeBody"]),
            ]
        )
    skill_table = Table(
        skill_table_data,
        colWidths=[1.2 * inch, 5.9 * inch],
        style=TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        ),
    )
    story.append(skill_table)

    story.append(section_heading("experience", styles))
    for entry in resume["experience"]:
        header = Table(
            [
                [
                    Paragraph(entry["company"], styles["ResumeRole"]),
                    Paragraph(f"{entry['location']}<br/>{entry['start']} - {entry['end']}", styles["ResumeBodyRight"]),
                ],
                [
                    Paragraph(entry["title"], styles["ResumeBody"]),
                    Paragraph(", ".join(entry["tools"]), styles["ResumeMeta"]),
                ],
            ],
            colWidths=[5.25 * inch, 2.25 * inch],
            style=TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            ),
        )
        story.append(header)
        story.append(Spacer(1, 0.05 * inch))
        story.append(bullet_flowable(entry["highlights"], styles["ResumeBody"], body_font))
        story.append(Spacer(1, 0.1 * inch))

    story.append(section_heading("selected projects", styles))
    for project in resume["projects"]:
        story.append(Paragraph(f"<b>{project['name']}</b> - {project['category']} ({project['date']})", styles["ResumeBody"]))
        story.append(Paragraph(", ".join(project["stack"]), styles["ResumeMeta"]))
        story.append(Paragraph(project["summary"], styles["ResumeBody"]))
        story.append(Spacer(1, 0.06 * inch))

    story.append(section_heading("education", styles))
    for entry in resume["education"]:
        story.append(Paragraph(f"<b>{entry['school']}</b>", styles["ResumeRole"]))
        story.append(Paragraph(entry["degree"], styles["ResumeBody"]))
        story.append(Paragraph(f"{entry['location']} | {entry['dates']}", styles["ResumeMeta"]))
        story.append(Paragraph(entry["coursework"], styles["ResumeBody"]))
        story.append(bullet_flowable(entry["highlights"], styles["ResumeBody"], body_font))
        story.append(Spacer(1, 0.06 * inch))

    story.append(section_heading("leadership", styles))
    leadership_lines = [
        f"<b>{entry['role']}</b> of {entry['organization']} <font color='#65558F'>{entry['dates']}</font>"
        for entry in resume["leadership"]
    ]
    story.append(bullet_flowable(leadership_lines, styles["ResumeBody"], body_font))

    return story


def build_pdf(resume_path: Path, output_path: Path) -> None:
    resume = load_resume(resume_path)
    body_font, bold_font = register_fonts()
    styles = paragraph_styles(body_font, bold_font)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=LETTER,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
        title=f"{resume['basics']['name']} Resume",
        author=resume['basics']['name'],
        subject="Resume",
        keywords=", ".join(resume.get("metadata", {}).get("keywords", ["resume", "portfolio"])),
    )

    story = build_story(resume, styles, body_font)

    def add_metadata(canvas, document):
        canvas.setTitle(f"{resume['basics']['name']} Resume")
        canvas.setAuthor(resume['basics']['name'])
        canvas.setSubject("Resume")
        canvas.setKeywords(", ".join(resume.get("metadata", {}).get("keywords", ["resume", "portfolio"])))

    doc.build(story, onFirstPage=add_metadata, onLaterPages=add_metadata)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="data/resume.json", help="Path to the resume JSON source")
    parser.add_argument("--output", default="media/Hayoung_Ryow_Resume.pdf", help="Path to the generated PDF")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_pdf(Path(args.input), Path(args.output))


if __name__ == "__main__":
    main()