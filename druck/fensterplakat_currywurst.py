#!/usr/bin/env python3
"""Fensterplakat „Currywurst mit Pommes“ für Die Bratküche.

Erzeugt eine druckfertige PDF:
  * Endformat A2 (andere A-Formate per --format), 2 mm Beschnitt rundum
    (wie beim Flyeralarm-Flyer), Schnitt- und Beschnittrahmen sind gesetzt
  * Hintergrund, Schrift und Linien in CMYK, Schriften eingebettet
  * QR-Code als Vektorgrafik (gleicher Link wie auf dem Vorbestell-Flyer)

Aufruf (im Ordner des Repositorys):
  python3 druck/fensterplakat_currywurst.py                     # Vorschau ohne Foto
  python3 druck/fensterplakat_currywurst.py --foto bild.jpg     # Druckdatei mit Foto
  python3 druck/fensterplakat_currywurst.py --foto bild.jpg --fokus 0.5,0.6 --format A1

--fokus x,y (0 bis 1) legt fest, welcher Teil des Fotos im Ausschnitt bleibt
(0.5,0.5 = Mitte, 0.5,0.7 = eher den unteren Bildteil zeigen).

Benötigt: reportlab, pillow, fonttools, brotli (pip install reportlab pillow fonttools brotli).
Die Schriften kommen aus assets/fonts (Bebas Neue, Fraunces, DM Sans, Caveat; SIL OFL).
"""

import argparse
import os
import sys
import tempfile

from PIL import Image, ImageOps
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Rect
from reportlab.lib.colors import CMYKColor
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FONT_SRC = os.path.join(REPO, "assets", "fonts")
FONT_CACHE = os.path.join(HERE, ".fonts")

# ---------------------------------------------------------------- Inhalte
WORDMARK = "DIE BRATKÜCHE"
CATEGORIES = ["SMASH BURGER", "LOADED FRIES", "CURRYWURST"]
KICKER = "BERLINER ART  ·  HAUSGEMACHTE CURRYSOSSE"
TITLE_1 = "Currywurst"
TITLE_2 = "mit Pommes"
DESCRIPTION = ["Currywurst ohne Darm mit hausgemachter Currysoße,",
               "dazu goldgelbe Pommes."]
PRICE = "8,50"
ORDER_URL = "https://su.onl/mfsri42"          # QR-Link vom Vorbestell-Flyer
ADDRESS = "LACHNERSTRASSE 2  ·  91058 ERLANGEN"
HOURS = [("MO – DO", "11–15 & 17–20 UHR"), ("FR", "11–15 UHR")]

# ---------------------------------------------------------------- Farben (CMYK)
# Angelehnt an die Website-Farben (assets/css/style.css). Gesamtfarbauftrag <= 270 %.
BG = CMYKColor(0.55, 0.55, 0.60, 1.00)          # warmes Tiefschwarz (#0C0A08)
GLOW = CMYKColor(0.40, 0.60, 0.80, 0.72)        # warmer Lichtschein hinter dem Foto
SURFACE = CMYKColor(0.45, 0.55, 0.65, 0.88)     # Platzhalter-Fläche (#191410)
CREAM = CMYKColor(0.02, 0.05, 0.14, 0.00)       # Text (#F5ECDC)
MUTED = CMYKColor(0.22, 0.25, 0.36, 0.06)       # Fließtext (#BCAF9A)
GOLD = CMYKColor(0.05, 0.26, 0.68, 0.02)        # Gold (#E7BE6B)
GOLD_LIGHT = CMYKColor(0.02, 0.16, 0.50, 0.00)  # helles Gold (#F4D48E)
GOLD_DEEP = CMYKColor(0.15, 0.40, 0.85, 0.08)   # dunkles Gold (#C8963F)
EMBER = CMYKColor(0.00, 0.62, 0.90, 0.00)       # Glut-Orange (#EE7A2C)
INK = CMYKColor(0.50, 0.55, 0.60, 0.95)         # dunkle Schrift auf Gold

FORMATS = {"A4": (210, 297), "A3": (297, 420), "A2": (420, 594),
           "A1": (594, 841), "A0": (841, 1189)}

# Gestaltet wird in Millimetern auf A2 (420 × 594 mm). Für andere A-Formate
# wird alles proportional skaliert, nur der Beschnitt bleibt bei 2 mm.
DESIGN_W, DESIGN_H = 420.0, 594.0

# Fotoausschnitt (in mm, von oben links gemessen, im A2-Raster)
PHOTO_X, PHOTO_Y, PHOTO_W, PHOTO_H, PHOTO_R = 30.0, 92.0, 360.0, 262.0, 6.0


# ---------------------------------------------------------------- Schriften
FONT_JOBS = {
    "bebas-neue-latin-400-normal.woff2": [("BebasNeue", None)],
    "fraunces-latin-wght-normal.woff2": [("Fraunces-Bold", 700), ("Fraunces-Black", 900)],
    "dm-sans-latin-wght-normal.woff2": [("DMSans-Regular", 400), ("DMSans-Medium", 500),
                                         ("DMSans-Bold", 700)],
    "caveat-latin-wght-normal.woff2": [("Caveat-Bold", 700)],
}


def build_fonts():
    """Wandelt die Web-Schriften der Website in feste TTF-Schnitte um (einmalig)."""
    os.makedirs(FONT_CACHE, exist_ok=True)
    todo = [(src, name, w) for src, jobs in FONT_JOBS.items() for name, w in jobs
            if not os.path.exists(os.path.join(FONT_CACHE, name + ".ttf"))]
    if todo:
        from fontTools.ttLib import TTFont as FTFont
        from fontTools.varLib import instancer
        for src, name, weight in todo:
            font = FTFont(os.path.join(FONT_SRC, src))
            if "fvar" in font:
                loc = {a.axisTag: (weight if a.axisTag == "wght" else a.defaultValue)
                       for a in font["fvar"].axes}
                font = instancer.instantiateVariableFont(font, loc)
            # Jeder Schnitt bekommt einen eigenen Namen, sonst verwechselt das PDF
            # z. B. „DM Sans Bold“ mit „DM Sans Regular“.
            nt = font["name"]
            for rec in list(nt.names):
                if rec.nameID in (16, 17, 21, 22, 25):
                    nt.removeNames(nameID=rec.nameID)
            nt.setName(name.replace("-", " "), 1, 3, 1, 0x409)
            nt.setName("Regular", 2, 3, 1, 0x409)
            nt.setName(name.replace("-", " "), 4, 3, 1, 0x409)
            nt.setName(name, 6, 3, 1, 0x409)
            nt.setName(name + "-Druck", 3, 3, 1, 0x409)
            nt.names = [r for r in nt.names if r.platformID == 3]
            font.flavor = None
            font.save(os.path.join(FONT_CACHE, name + ".ttf"))
    for jobs in FONT_JOBS.values():
        for name, _ in jobs:
            pdfmetrics.registerFont(TTFont(name, os.path.join(FONT_CACHE, name + ".ttf")))


# ---------------------------------------------------------------- Zeichenhilfen
class Poster:
    def __init__(self, path, fmt="A2", bleed=2.0):
        tw, th = FORMATS[fmt]
        self.s = tw / DESIGN_W                     # Skalierung gegenüber A2
        self.bleed = bleed
        self.page_w, self.page_h = (tw + 2 * bleed) * mm, (th + 2 * bleed) * mm
        # Startschrift = eingebettete Hausschrift, damit keine nicht eingebettete
        # Standardschrift (Helvetica) in der Datei steht; nur CMYK-Farben zulassen.
        self.c = canvas.Canvas(path, pagesize=(self.page_w, self.page_h),
                               initialFontName="DMSans-Regular", initialFontSize=12,
                               enforceColorSpace="cmyk")
        self.c.setTitle("Die Bratküche – Fensterplakat Currywurst mit Pommes")
        self.c.setAuthor("Die Bratküche Erlangen")
        self.c.setSubject(f"Plakat {fmt} ({tw} × {th} mm), {bleed:g} mm Beschnitt")
        b = bleed * mm
        self.c.setTrimBox((b, b, self.page_w - b, self.page_h - b))
        self.c.setBleedBox((0, 0, self.page_w, self.page_h))
        self.c.setArtBox((b, b, self.page_w - b, self.page_h - b))

    # Design-Millimeter (A2, von oben links) -> PDF-Punkte
    def X(self, x):
        return (self.bleed + x * self.s) * mm

    def Y(self, y):
        return self.page_h - (self.bleed + y * self.s) * mm

    def L(self, v):
        return v * self.s * mm

    def text(self, s, x, y, font, size, color, tracking=0.0, align="center"):
        """Text mit Laufweite (tracking in em). x/y/size in Design-mm, y = Grundlinie."""
        c = self.c
        fs = self.L(size)
        w = self.text_width(s, font, size, tracking)
        if align == "center":
            x0 = self.X(x) - w / 2
        elif align == "right":
            x0 = self.X(x) - w
        else:
            x0 = self.X(x)
        t = c.beginText()
        t.setTextOrigin(x0, self.Y(y))
        t.setFont(font, fs)
        t.setCharSpace(tracking * fs)
        t.setFillColor(color)
        t.textLine(s)
        c.drawText(t)
        return w

    def text_width(self, s, font, size, tracking=0.0):
        fs = self.L(size)
        return pdfmetrics.stringWidth(s, font, fs) + tracking * fs * max(len(s) - 1, 0)

    def fit_size(self, s, font, max_w, start, tracking=0.0):
        size = start
        while self.text_width(s, font, size, tracking) > self.L(max_w) and size > 1:
            size -= 0.25
        return size

    def diamond(self, x, y, r, color):
        c = self.c
        p = c.beginPath()
        cx, cy, rr = self.X(x), self.Y(y), self.L(r)
        p.moveTo(cx, cy + rr)
        p.lineTo(cx + rr, cy)
        p.lineTo(cx, cy - rr)
        p.lineTo(cx - rr, cy)
        p.close()
        c.setFillColor(color)
        c.drawPath(p, stroke=0, fill=1)

    def hline(self, x1, x2, y, color, width=0.35):
        c = self.c
        c.setStrokeColor(color)
        c.setLineWidth(self.L(width))
        c.line(self.X(x1), self.Y(y), self.X(x2), self.Y(y))


# ---------------------------------------------------------------- Bausteine
def draw_background(p):
    c = p.c
    c.setFillColor(BG)
    c.rect(0, 0, p.page_w, p.page_h, stroke=0, fill=1)
    # warmer Lichtschein hinter dem Foto (wie das Spotlight auf dem Flyer)
    c.saveState()
    path = c.beginPath()
    path.rect(0, 0, p.page_w, p.page_h)
    c.clipPath(path, stroke=0, fill=0)
    c.radialGradient(p.X(210), p.Y(215), p.L(330), [GLOW, BG], extend=True)
    c.restoreState()
    # feiner Goldrahmen wie auf der Speisekarte
    c.setStrokeColor(GOLD_DEEP)
    c.setLineWidth(p.L(0.45))
    inset = 13.0
    c.roundRect(p.X(inset), p.Y(DESIGN_H - inset), p.L(DESIGN_W - 2 * inset),
                p.L(DESIGN_H - 2 * inset), p.L(5), stroke=1, fill=0)


def draw_header(p):
    size = p.fit_size(WORDMARK, "BebasNeue", 300, 36, tracking=0.10)
    p.text(WORDMARK, 210, 57, "BebasNeue", size, CREAM, tracking=0.10)

    # Zeile „SMASH BURGER ◆ LOADED FRIES ◆ CURRYWURST“
    fs, tr, gap = 4.6, 0.32, 12.0
    widths = [p.text_width(t, "DMSans-Bold", fs, tr) / (p.s * mm) for t in CATEGORIES]
    total = sum(widths) + gap * 2 * (len(CATEGORIES) - 1)
    x = 210 - total / 2
    for i, (t, w) in enumerate(zip(CATEGORIES, widths)):
        color = GOLD_LIGHT if t == "CURRYWURST" else MUTED
        p.text(t, x, 71, "DMSans-Bold", fs, color, tracking=tr, align="left")
        x += w
        if i < len(CATEGORIES) - 1:
            p.diamond(x + gap, 69.4, 1.3, EMBER)
            x += 2 * gap


def draw_bowl_icon(p, cx, cy, size, color, width=0.9):
    """Currywurst-Schale wie auf der Speisekarte (Linienzeichnung), size = Breite in mm."""
    c = p.c
    u = size / 10.0
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(p.L(width))
    c.setLineJoin(1)
    c.setLineCap(1)
    # Schale (Trapez)
    path = c.beginPath()
    path.moveTo(p.X(cx - 5 * u), p.Y(cy - 0.6 * u))
    path.lineTo(p.X(cx + 5 * u), p.Y(cy - 0.6 * u))
    path.lineTo(p.X(cx + 3.6 * u), p.Y(cy + 3.6 * u))
    path.lineTo(p.X(cx - 3.6 * u), p.Y(cy + 3.6 * u))
    path.close()
    c.drawPath(path, stroke=1, fill=0)
    # drei Wurststücke
    for dx in (-2.6, 0, 2.6):
        c.circle(p.X(cx + dx * u), p.Y(cy - 2.0 * u), p.L(1.3 * u), stroke=1, fill=0)
    # Pommes-Piker
    c.line(p.X(cx + 1.4 * u), p.Y(cy - 3.3 * u), p.X(cx + 4.0 * u), p.Y(cy - 6.2 * u))
    c.restoreState()


def rounded_clip(p, x, y, w, h, r):
    c = p.c
    path = c.beginPath()
    path.roundRect(p.X(x), p.Y(y + h), p.L(w), p.L(h), p.L(r))
    c.clipPath(path, stroke=0, fill=0)


def prepare_photo(src, focus, target_w_mm, target_h_mm, max_ppi=240):
    """Dreht nach EXIF, schneidet auf das Seitenverhältnis zu und speichert ein JPEG."""
    img = Image.open(src)
    img = ImageOps.exif_transpose(img).convert("RGB")
    W, H = img.size
    ratio = target_w_mm / target_h_mm
    if W / H > ratio:
        cw, ch = int(round(H * ratio)), H
    else:
        cw, ch = W, int(round(W / ratio))
    fx, fy = focus
    left = min(max(int(fx * W - cw / 2), 0), W - cw)
    top = min(max(int(fy * H - ch / 2), 0), H - ch)
    img = img.crop((left, top, left + cw, top + ch))
    max_px = int(target_w_mm / 25.4 * max_ppi)
    if img.width > max_px:
        img = img.resize((max_px, int(round(max_px / ratio))), Image.LANCZOS)
    ppi = img.width / (target_w_mm / 25.4)
    fd, tmp = tempfile.mkstemp(suffix=".jpg")
    os.close(fd)
    img.save(tmp, "JPEG", quality=93, subsampling=0, dpi=(ppi, ppi))
    return tmp, img.size, ppi


def draw_photo(p, photo, focus):
    c = p.c
    x, y, w, h, r = PHOTO_X, PHOTO_Y, PHOTO_W, PHOTO_H, PHOTO_R
    info = None
    c.saveState()
    rounded_clip(p, x, y, w, h, r)
    if photo:
        tmp, size, ppi = prepare_photo(photo, focus, w * p.s, h * p.s)
        c.drawImage(tmp, p.X(x), p.Y(y + h), p.L(w), p.L(h))
        os.remove(tmp)
        info = (size, ppi)
    else:
        c.setFillColor(SURFACE)
        c.rect(p.X(x), p.Y(y + h), p.L(w), p.L(h), stroke=0, fill=1)
        c.setStrokeColor(GOLD_DEEP)
        c.setLineWidth(p.L(0.6))
        c.setDash(p.L(4), p.L(3))
        c.roundRect(p.X(x + 9), p.Y(y + h - 9), p.L(w - 18), p.L(h - 18), p.L(4), stroke=1, fill=0)
        c.setDash()
        draw_bowl_icon(p, x + w / 2, y + h / 2 - 22, 46, GOLD, width=1.4)
        p.text("FOTO FOLGT", x + w / 2, y + h / 2 + 30, "BebasNeue", 22, GOLD, tracking=0.12)
        p.text("Hier kommt das Foto von Currywurst & Pommes hin",
               x + w / 2, y + h / 2 + 44, "DMSans-Medium", 6.2, MUTED)
    c.restoreState()
    # Goldkante
    c.setStrokeColor(GOLD_DEEP)
    c.setLineWidth(p.L(0.6))
    c.roundRect(p.X(x), p.Y(y + h), p.L(w), p.L(h), p.L(r), stroke=1, fill=0)
    return info


def draw_new_badge(p, cx=62.0, cy=104.0, r=40.0):
    c = p.c
    c.saveState()
    c.translate(p.X(cx), p.Y(cy))
    c.rotate(10)
    # Schatten-Ring in Hintergrundfarbe, damit der Stempel sich vom Foto löst
    c.setFillColor(BG)
    c.circle(0, 0, p.L(r + 2.2), stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.circle(0, 0, p.L(r), stroke=0, fill=1)
    c.setStrokeColor(INK)
    c.setLineWidth(p.L(0.6))
    c.circle(0, 0, p.L(r - 3.2), stroke=1, fill=0)

    def ctext(s, dy, font, size, color, tracking=0.0):
        fs = p.L(size)
        w = pdfmetrics.stringWidth(s, font, fs) + tracking * fs * (len(s) - 1)
        t = c.beginText()
        t.setTextOrigin(-w / 2, -p.L(dy))
        t.setFont(font, fs)
        t.setCharSpace(tracking * fs)
        t.setFillColor(color)
        t.textLine(s)
        c.drawText(t)

    ctext("AB SOFORT", -18.0, "DMSans-Bold", 4.2, INK, tracking=0.25)
    ctext("NEU", 11.0, "BebasNeue", 34, INK, tracking=0.04)
    ctext("bei uns!", 23.5, "Caveat-Bold", 10.0, INK)
    c.restoreState()


def draw_price_badge(p, cx=352.0, cy=338.0, r=42.0):
    c = p.c
    c.saveState()
    c.translate(p.X(cx), p.Y(cy))
    c.rotate(-6)
    c.setFillColor(BG)
    c.circle(0, 0, p.L(r), stroke=0, fill=1)
    c.setStrokeColor(GOLD)
    c.setLineWidth(p.L(1.4))
    c.circle(0, 0, p.L(r - 1.6), stroke=1, fill=0)
    c.setStrokeColor(GOLD_DEEP)
    c.setLineWidth(p.L(0.4))
    c.circle(0, 0, p.L(r - 5.0), stroke=1, fill=0)

    def ctext(s, dy, font, size, color, tracking=0.0, dx=0.0):
        fs = p.L(size)
        w = pdfmetrics.stringWidth(s, font, fs) + tracking * fs * (len(s) - 1)
        t = c.beginText()
        t.setTextOrigin(-w / 2 + p.L(dx), -p.L(dy))
        t.setFont(font, fs)
        t.setCharSpace(tracking * fs)
        t.setFillColor(color)
        t.textLine(s)
        c.drawText(t)
        return w

    ctext("NUR", -17.5, "DMSans-Bold", 4.8, GOLD, tracking=0.3)
    ctext(PRICE, 12.0, "BebasNeue", 34, GOLD_LIGHT, tracking=0.02)
    ctext("EURO", 22.5, "DMSans-Bold", 4.8, GOLD, tracking=0.3)
    c.restoreState()


def draw_title(p):
    # Dachzeile mit Schalen-Symbol
    fs, tr = 5.4, 0.26
    p.text(KICKER, 210, 384, "DMSans-Bold", fs, GOLD, tracking=tr)

    s1 = p.fit_size(TITLE_1, "Fraunces-Black", 340, 76)
    p.text(TITLE_1, 210, 442, "Fraunces-Black", s1, CREAM)
    s2 = min(s1 * 0.66, p.fit_size(TITLE_2, "Fraunces-Bold", 300, 60))
    p.text(TITLE_2, 210, 484, "Fraunces-Bold", s2, GOLD)

    for i, line in enumerate(DESCRIPTION):
        p.text(line, 210, 507 + i * 11.5, "DMSans-Regular", 8.4, MUTED)


def draw_footer(p):
    p.hline(30, 390, 534, GOLD_DEEP, 0.3)
    p.diamond(210, 534, 1.6, GOLD)

    # QR-Code zum Vorbestellen
    qx, qy, qs, pad = 30.0, 542.0, 34.0, 3.6
    c = p.c
    c.setFillColor(CREAM)
    c.roundRect(p.X(qx), p.Y(qy + qs), p.L(qs), p.L(qs), p.L(2.5), stroke=0, fill=1)
    # Die Module werden als ein einziger Vektorpfad gezeichnet (keine Haarlinien,
    # keine RGB-Voreinstellungen aus dem Grafik-Renderer).
    widget = QrCodeWidget(ORDER_URL, barLevel="M", barBorder=0)
    x1, y1, x2, y2 = widget.getBounds()
    inner = p.L(qs - 2 * pad)
    k = inner / (x2 - x1)
    ox, oy = p.X(qx + pad), p.Y(qy + qs - pad)
    path = c.beginPath()

    def collect(node):
        for child in getattr(node, "contents", []):
            if isinstance(child, Rect):
                if child.fillColor != widget.barFillColor:
                    continue                     # weiße Hintergrundfläche weglassen
                path.rect(ox + (child.x - x1) * k, oy + (child.y - y1) * k,
                          child.width * k, child.height * k)
            else:
                collect(child)

    collect(widget.draw())
    c.setFillColor(INK)
    c.drawPath(path, stroke=0, fill=1)

    tx = qx + qs + 8
    p.text("JETZT ONLINE VORBESTELLEN", tx, qy + 12, "BebasNeue", 10.5, GOLD,
           tracking=0.06, align="left")
    p.text("QR-Code scannen – frisch & ohne", tx, qy + 21, "DMSans-Regular", 4.9, MUTED,
           align="left")
    p.text("Wartezeit abholen.", tx, qy + 27.5, "DMSans-Regular", 4.9, MUTED, align="left")

    # Öffnungszeiten und Adresse rechts
    rx = 390.0
    y = qy + 10
    for day, time in HOURS:
        wt = p.text(time, rx, y, "BebasNeue", 10.5, CREAM, tracking=0.04, align="right")
        p.text(day, rx - wt / (p.s * mm) - 4, y, "BebasNeue", 10.5, GOLD, tracking=0.06,
               align="right")
        y += 10.5
    p.text(ADDRESS, rx, qy + 31.5, "DMSans-Bold", 4.2, MUTED, tracking=0.22, align="right")


def build(out, photo=None, focus=(0.5, 0.5), fmt="A2", bleed=2.0):
    build_fonts()
    p = Poster(out, fmt, bleed)
    draw_background(p)
    draw_header(p)
    info = draw_photo(p, photo, focus)
    draw_new_badge(p)
    draw_price_badge(p)
    draw_title(p)
    draw_footer(p)
    p.c.showPage()
    p.c.save()
    return info


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--foto", help="Foto von Currywurst & Pommes (JPG/PNG/HEIC als JPG)")
    ap.add_argument("--fokus", default="0.5,0.5", help="Bildausschnitt x,y zwischen 0 und 1")
    ap.add_argument("--format", default="A2", choices=sorted(FORMATS))
    ap.add_argument("--beschnitt", type=float, default=2.0, help="Beschnitt in mm (Standard 2)")
    ap.add_argument("--out", help="Ausgabedatei (PDF)")
    a = ap.parse_args()

    focus = tuple(float(v) for v in a.fokus.split(","))
    tw, th = FORMATS[a.format]
    kind = "Druckdatei" if a.foto else "VORSCHAU_ohne_Foto"
    out = a.out or os.path.join(
        HERE, f"Bratkueche_Fensterplakat_Currywurst_{a.format}_{kind}.pdf")
    info = build(out, a.foto, focus, a.format, a.beschnitt)
    print(f"Gespeichert: {out}")
    print(f"Format: {a.format} {tw} × {th} mm, Datenformat "
          f"{tw + 2 * a.beschnitt:g} × {th + 2 * a.beschnitt:g} mm ({a.beschnitt:g} mm Beschnitt)")
    if info:
        (pw, ph), ppi = info
        note = "gut" if ppi >= 150 else ("ausreichend fürs Fenster" if ppi >= 100 else "ZU NIEDRIG")
        print(f"Foto: {pw} × {ph} px im Ausschnitt, {ppi:.0f} ppi im Druck ({note})")
        if ppi < 100:
            sys.exit(2)


if __name__ == "__main__":
    main()
