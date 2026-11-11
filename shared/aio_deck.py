"""Shared helpers for AIO2026 lecture decks built from "Template Format trình bày.pptx".

Every slide is a clone of one of the template's three sample slides (title, outline, content), so the
logo, header bar, page number and Times New Roman typography stay exactly as in the template.
Used by kafka/architecture-slides/build_deck.py and databrick/governance-slides/build_deck.py.
"""
from __future__ import annotations

import copy
import glob
import os
import re
import sys

from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt


FONT = "Times New Roman"
MONO = "Courier New"
ORANGE = RGBColor(0xC5, 0x5A, 0x11)   # template section titles
BLUE = RGBColor(0x00, 0x70, 0xC0)     # template "❖" headings
GREEN = RGBColor(0x53, 0x81, 0x35)    # template outline bar
GREEN_LIGHT = RGBColor(0xE2, 0xF0, 0xD9)
PEACH = RGBColor(0xFB, 0xE4, 0xD4)    # template outline boxes
PEACH_ACTIVE = RGBColor(0xF4, 0xB0, 0x81)
GOLD = RGBColor(0xBF, 0x90, 0x00)
PURPLE = RGBColor(0x70, 0x30, 0xA0)
OUT_BLUE = RGBColor(0x0B, 0x53, 0x94)
INK = RGBColor(0x26, 0x26, 0x26)
GRAY = RGBColor(0x75, 0x75, 0x75)
CODE_BG = RGBColor(0xF5, 0xF5, 0xF5)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

def find_template(workspace: str) -> str:
    """The AIO2026 presentation template sits in the workspace root as 'Template Format trình bày.pptx'."""
    hits = glob.glob(os.path.join(workspace, "Template Format*.pptx"))
    if len(hits) != 1:
        sys.exit(f"Expected one 'Template Format*.pptx' in {workspace}, found {hits}")
    return hits[0]


# --------------------------------------------------------------------------- cloning
def clone_slide(prs, src):
    """Append a copy of `src` (same layout, same shapes, images and links re-related)."""
    new = prs.slides.add_slide(src.slide_layout)
    for ph in list(new.placeholders):
        ph._element.getparent().remove(ph._element)
    rid_map = {}
    for rid, rel in src.part.rels.items():
        if rel.reltype in (RT.SLIDE_LAYOUT, RT.NOTES_SLIDE):
            continue
        if rel.is_external:
            rid_map[rid] = new.part.relate_to(rel.target_ref, rel.reltype, is_external=True)
        else:
            rid_map[rid] = new.part.relate_to(rel.target_part, rel.reltype)
    attrs = [qn("r:embed"), qn("r:id"), qn("r:link")]
    for el in src.shapes._spTree.iterchildren():
        if el.tag in (qn("p:nvGrpSpPr"), qn("p:grpSpPr")):
            continue
        dup = copy.deepcopy(el)
        for node in dup.iter():
            for a in attrs:
                if node.get(a) in rid_map:
                    node.set(a, rid_map[node.get(a)])
        new.shapes._spTree.append(dup)
    return new


def shape_by_name(slide, name):
    for shp in slide.shapes:
        if shp.name == name:
            return shp
    raise KeyError(name)


def set_text_keep_format(shape, text):
    """Replace the text of the first run, drop the other runs/paragraphs."""
    tf = shape.text_frame
    first = tf.paragraphs[0]
    for p in tf.paragraphs[1:]:
        p._p.getparent().remove(p._p)
    runs = first.runs
    runs[0].text = text
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


def remove_shape(shape):
    shape._element.getparent().remove(shape._element)


# --------------------------------------------------------------------------- text helpers
TOKEN = re.compile(r"(\*\*.+?\*\*|`.+?`)")


def add_runs(paragraph, text, size, color=INK, bold=False):
    for part in TOKEN.split(text):
        if not part:
            continue
        run = paragraph.add_run()
        if part.startswith("**"):
            run.text, b, face = part[2:-2], True, FONT
        elif part.startswith("`"):
            run.text, b, face = part[1:-1], bold, MONO
        else:
            run.text, b, face = part, bold, FONT
        f = run.font
        f.name, f.size, f.bold = face, Pt(size - 1 if face == MONO else size), b
        f.color.rgb = color


def set_bullet(paragraph, level=0, char="•", color=BLUE, space_before=6):
    pPr = paragraph._p.get_or_add_pPr()
    indent = Emu(Inches(0.28))
    pPr.set("marL", str(int(indent * (level + 1))))
    pPr.set("indent", str(-int(indent)))
    for tag in ("a:spcBef", "a:buClr", "a:buFont", "a:buChar", "a:buNone"):
        for old in pPr.findall(qn(tag)):
            pPr.remove(old)
    spc = etree.SubElement(pPr, qn("a:spcBef"))
    etree.SubElement(spc, qn("a:spcPts"), val=str(space_before * 100))
    clr = etree.SubElement(pPr, qn("a:buClr"))
    etree.SubElement(clr, qn("a:srgbClr"), val=str(color))
    etree.SubElement(pPr, qn("a:buFont"), typeface="Arial")
    etree.SubElement(pPr, qn("a:buChar"), char=char)


def set_spacing(paragraph, before=6):
    pPr = paragraph._p.get_or_add_pPr()
    for old in pPr.findall(qn("a:spcBef")):
        pPr.remove(old)
    spc = etree.SubElement(pPr, qn("a:spcBef"))
    etree.SubElement(spc, qn("a:spcPts"), val=str(before * 100))
    pPr.insert(0, spc)


def textbox(slide, x, y, w, h, name):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    return tb


def bullets(slide, x, y, w, h, items, size=18, name="Bullets"):
    """items: str (level 0), ("sub", str) for level 1, ("plain", str) without bullet."""
    tb = textbox(slide, x, y, w, h, name)
    tf = tb.text_frame
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        kind, text = ("bullet", item) if isinstance(item, str) else item
        if kind == "sub":
            set_bullet(p, level=1, char="–", color=GRAY, space_before=2)
            add_runs(p, text, size - 2)
        elif kind == "plain":
            set_spacing(p, 6)
            add_runs(p, text, size)
        elif kind == "num":
            num, body = text
            set_spacing(p, 8)
            add_runs(p, f"**{num}.** {body}", size)
        else:
            set_bullet(p)
            add_runs(p, text, size)
    return tb


def callout(slide, x, y, w, h, text, kind="key", size=16, name="Callout"):
    fill, line = (GREEN_LIGHT, GREEN) if kind == "key" else (PEACH, ORANGE)
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.name = name
    shp.adjustments[0] = 0.08
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.line.color.rgb = line
    shp.line.width = Pt(1)
    shp.shadow.inherit = False
    tf = shp.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Inches(0.15)
    for i, para in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        add_runs(p, para, size)
    return shp


def caption(slide, x, y, w, text, name="Source"):
    tb = textbox(slide, x, y, w, 0.3, name)
    p = tb.text_frame.paragraphs[0]
    add_runs(p, text, 11, color=GRAY)
    for r in p.runs:
        r.font.italic = True
    return tb


def code_box(slide, x, y, w, title, text, kind="out", size=13, name="Lab output"):
    """Title bar plus monospaced body; kind 'out' (blue, lab output) or 'cmd' (green, command/data)."""
    bar_color = OUT_BLUE if kind == "out" else GREEN
    lines = text.split("\n")
    bar_h = 0.34
    body_h = 0.16 + len(lines) * size * 1.18 / 72
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(bar_h))
    bar.name = name + " title"
    bar.fill.solid()
    bar.fill.fore_color.rgb = bar_color
    bar.line.color.rgb = bar_color
    bar.shadow.inherit = False
    tf = bar.text_frame
    tf.margin_left = Inches(0.1)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    add_runs(p, title, 13, color=WHITE, bold=True)
    body = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y + bar_h), Inches(w), Inches(body_h))
    body.name = name
    body.fill.solid()
    body.fill.fore_color.rgb = CODE_BG
    body.line.color.rgb = bar_color
    body.line.width = Pt(0.75)
    body.shadow.inherit = False
    tf = body.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = tf.margin_right = Inches(0.1)
    tf.margin_top = tf.margin_bottom = Inches(0.06)
    for i, line in enumerate(lines):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = PP_ALIGN.LEFT
        run = para.add_run()
        run.text = line if line else " "
        run.font.name, run.font.size, run.font.color.rgb = MONO, Pt(size), INK
    return y + bar_h + body_h


def picture(slide, path, x, y, w, h, name="Figure"):
    """Fit an image inside the box (x, y, w, h), centred, keeping its aspect ratio."""
    with Image.open(path) as im:
        iw, ih = im.size
    scale = min(w / iw, h / ih)
    pw, ph = iw * scale, ih * scale
    pic = slide.shapes.add_picture(path, Inches(x + (w - pw) / 2), Inches(y + (h - ph) / 2), Inches(pw), Inches(ph))
    pic.name = name
    return pic


def table(slide, x, y, widths, rows, size=16, header_fill=GREEN, name="Table", row_h=0.42):
    n_rows, n_cols = len(rows), len(rows[0])
    shp = slide.shapes.add_table(n_rows, n_cols, Inches(x), Inches(y), Inches(sum(widths)), Inches(row_h * n_rows))
    shp.name = name
    tbl = shp.table
    tblPr = shp._element.graphic.graphicData.tbl.tblPr
    tblPr.set("firstRow", "1")
    tblPr.set("bandRow", "0")
    for j, wdt in enumerate(widths):
        tbl.columns[j].width = Inches(wdt)
    for i, row in enumerate(rows):
        tbl.rows[i].height = Inches(row_h)
        for j, value in enumerate(row):
            cell = tbl.cell(i, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = header_fill if i == 0 else (WHITE if i % 2 else RGBColor(0xF3, 0xF7, 0xEF))
            cell.margin_left = cell.margin_right = Inches(0.08)
            cell.margin_top = cell.margin_bottom = Inches(0.04)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            if i == 0:
                add_runs(p, value, size, color=WHITE, bold=True)
            else:
                add_runs(p, value, size)
    return shp


def box(slide, x, y, w, h, text, fill=GREEN_LIGHT, line=GREEN, size=16, bold=False, color=INK, name="Box", shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    shp = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.name = name
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        shp.adjustments[0] = 0.12
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.line.color.rgb = line
    shp.line.width = Pt(1.25)
    shp.shadow.inherit = False
    tf = shp.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Inches(0.05)
    for i, para in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        add_runs(p, para, size, color=color, bold=bold)
    return shp


def arrow(slide, x1, y1, x2, y2, color=GREEN, width=2.0, dashed=False, name="Arrow"):
    conn = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    conn.name = name
    conn.line.color.rgb = color
    conn.line.width = Pt(width)
    ln = conn.line._get_or_add_ln()
    if dashed:
        etree.SubElement(ln, qn("a:prstDash"), val="dash")
    etree.SubElement(ln, qn("a:tailEnd"), type="triangle", w="med", len="med")
    return conn


def label(slide, x, y, w, text, size=14, color=INK, bold=False, align=PP_ALIGN.CENTER, h=0.35, name="Label"):
    tb = textbox(slide, x, y, w, h, name)
    p = tb.text_frame.paragraphs[0]
    p.alignment = align
    add_runs(p, text, size, color=color, bold=bold)
    return tb


# --------------------------------------------------------------------------- deck
class Deck:
    """Clones the three sample slides of the template: title, outline (4 sections) and content."""

    def __init__(self, template, sections):
        if len(sections) != 4:
            raise ValueError("The template outline has exactly four section boxes.")
        self.sections = list(sections)
        self.prs = Presentation(template)
        self.proto_title, self.proto_outline, self.proto_content = list(self.prs.slides)[:3]
        self.n_template = len(self.prs.slides)

    def notes(self, slide, text):
        slide.notes_slide.notes_text_frame.text = text

    def title_slide(self, title, subtitle, author, note):
        s = clone_slide(self.prs, self.proto_title)
        set_text_keep_format(shape_by_name(s, "Google Shape;92;p1"), title)
        set_text_keep_format(shape_by_name(s, "Google Shape;93;p1"), subtitle)
        set_text_keep_format(shape_by_name(s, "Google Shape;95;p1"), author)
        self.notes(s, note)
        return s

    def outline(self, active, image, note):
        s = clone_slide(self.prs, self.proto_outline)
        names = ["Google Shape;102;p2", "Google Shape;103;p2", "Google Shape;104;p2", "Google Shape;108;p2"]
        for i, nm in enumerate(names):
            shp = shape_by_name(s, nm)
            set_text_keep_format(shp, self.sections[i])
            shp.left = Emu(876348)
            shp.width = Emu(5647544 if i == active else 5071279)
            shp.fill.solid()
            shp.fill.fore_color.rgb = PEACH_ACTIVE if i == active else PEACH
            for r in shp.text_frame.paragraphs[0].runs:
                r.font.size = Pt(30 if i == active else 26)
                r.font.bold = i == active
        remove_shape(shape_by_name(s, "Google Shape;110;p2"))
        picture(s, image, 7.45, 1.5, 5.5, 5.5, name="Section illustration")
        self.notes(s, note)
        return s

    def content(self, section, heading, note):
        s = clone_slide(self.prs, self.proto_content)
        set_text_keep_format(shape_by_name(s, "Google Shape;116;p3"), section)
        heading_box = shape_by_name(s, "Google Shape;115;p3")
        set_text_keep_format(heading_box, heading)
        heading_box.width = Inches(12.9)  # template box is 6.7"; long topics would wrap onto the content
        self.notes(s, note)
        return s

    def finish(self, path):
        sld_ids = self.prs.slides._sldIdLst
        for sld_id in list(sld_ids)[: self.n_template]:
            self.prs.part.drop_rel(sld_id.get(qn("r:id")))
            sld_ids.remove(sld_id)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.prs.save(path)
