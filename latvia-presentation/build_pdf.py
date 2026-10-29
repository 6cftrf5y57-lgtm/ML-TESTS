#!/usr/bin/env python3
"""3-page A4 landscape presentation PDF on the history of Latvia (v2, grid-aligned)."""

import os
from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets_tiny")
FONTS = os.path.join(BASE, "fonts")
OUT = os.path.join(BASE, "History_of_Latvia.pdf")

PAGE_W, PAGE_H = landscape(A4)

CARMINE = HexColor("#9E1B32")
CARMINE_DARK = HexColor("#7A1426")
WHITE = HexColor("#FFFFFF")
INK = HexColor("#241f20")
GOLD = HexColor("#C9A227")
CREAM = HexColor("#F7F2E9")
GRAY = HexColor("#6f6a66")

pdfmetrics.registerFont(TTFont("DVS", os.path.join(FONTS, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DVS-Bold", os.path.join(FONTS, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DVS-Obl", os.path.join(FONTS, "DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFont(TTFont("DVSerif-Bold", os.path.join(FONTS, "DejaVuSerif-Bold.ttf")))

M = 14 * mm
HEADER_H = 17 * mm
FOOTER_H = 9 * mm
CONTENT_TOP = PAGE_H - HEADER_H
CONTENT_BOTTOM = FOOTER_H
GUTTER = 8 * mm


def img_wh(path):
    w, h = Image.open(path).size
    return w, h


def draw_image_box(c, path, x, y_top, box_w, box_h, caption=None, caption_size=7.5):
    """Draw image centered inside the box (x, y_top-box_h, box_w, box_h); caption below the box."""
    pw, ph = img_wh(path)
    scale = min(box_w / pw, box_h / ph)
    w, h = pw * scale, ph * scale
    dx = x + (box_w - w) / 2
    dy = y_top - box_h + (box_h - h) / 2
    c.setFillColor(WHITE)
    c.setStrokeColor(HexColor("#d9c9b8"))
    c.setLineWidth(0.8)
    c.roundRect(dx - 3, dy - 3, w + 6, h + 6, 4, stroke=1, fill=1)
    c.drawImage(ImageReader(path), dx, dy, w, h, preserveAspectRatio=True, mask="auto")
    if caption:
        c.setFont("DVS-Obl", caption_size)
        c.setFillColor(GRAY)
        c.drawString(x, y_top - box_h - 4 * mm, caption)
    return y_top - box_h - (7 * mm if caption else 0)


def flag_badge(c, x, y, w, h):
    c.setFillColor(CARMINE)
    c.rect(x, y + h * 0.6, w, h * 0.4, stroke=0, fill=1)
    c.rect(x, y, w, h * 0.4, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.rect(x, y + h * 0.4, w, h * 0.2, stroke=0, fill=1)
    c.setStrokeColor(HexColor("#d8cfc0"))
    c.setLineWidth(0.6)
    c.rect(x, y, w, h, stroke=1, fill=0)


def header(c, kicker, title, page_no, total=3):
    c.setFillColor(CARMINE)
    c.rect(0, PAGE_H - HEADER_H + 1 * mm, PAGE_W, HEADER_H - 1 * mm, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.rect(0, PAGE_H - HEADER_H, PAGE_W, 1 * mm, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.setFont("DVS-Bold", 10)
    c.drawString(M, PAGE_H - 7.6 * mm, kicker.upper())
    c.setFont("DVSerif-Bold", 20)
    c.drawString(M, PAGE_H - 14.4 * mm, title)
    flag_badge(c, PAGE_W - M - 32, PAGE_H - 14 * mm, 32, 17)
    c.setFont("DVS", 9)
    c.setFillColor(HexColor("#f3dfe3"))
    c.drawRightString(PAGE_W - M - 40, PAGE_H - 9 * mm, f"{page_no} / {total}")


def footer(c, note):
    c.setStrokeColor(HexColor("#e3dccf"))
    c.setLineWidth(0.7)
    c.line(M, FOOTER_H - 1.5 * mm, PAGE_W - M, FOOTER_H - 1.5 * mm)
    c.setFillColor(GRAY)
    c.setFont("DVS", 7.5)
    c.drawString(M, FOOTER_H - 5 * mm, note)
    c.drawRightString(PAGE_W - M, FOOTER_H - 5 * mm, "The History of Latvia")


def section_label(c, x, y, text, size=11):
    c.setFillColor(CARMINE)
    c.setFont("DVS-Bold", size)
    c.drawString(x, y, text.upper())
    w = pdfmetrics.stringWidth(text.upper(), "DVS-Bold", size)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.line(x, y - 2.5, x + w, y - 2.5)
    return y - 7 * mm


def wrap(text, max_w, font, size):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if pdfmetrics.stringWidth(t, font, size) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def bullets(c, x, y, width, items, size=10, leading=13.5, gap=4.5):
    for head, body in items:
        c.setFillColor(CARMINE)
        c.setFont("DVS-Bold", size)
        c.drawString(x, y, "\u25a0")
        tx = x + 10
        c.setFillColor(INK)
        c.setFont("DVS", size)
        if head:
            c.setFont("DVS-Bold", size)
            c.drawString(tx, y, head)
            hw = pdfmetrics.stringWidth(head + " ", "DVS-Bold", size)
            c.setFont("DVS", size)
            lines = wrap(body, width - 10 - hw, "DVS", size)
            if lines:
                c.drawString(tx + hw, y, lines[0])
                y -= leading
                for ln in lines[1:]:
                    c.drawString(tx, y, ln)
                    y -= leading
        else:
            lines = wrap(body, width - 10, "DVS", size)
            for ln in lines:
                c.drawString(tx, y, ln)
                y -= leading
        y -= gap
    return y


def timeline(c, x, y_line, width, events, size=9):
    n = len(events)
    step = width / (n - 1)
    c.setStrokeColor(HexColor("#cbb98a"))
    c.setLineWidth(2)
    c.line(x, y_line, x + width, y_line)
    for i, (yr, txt) in enumerate(events):
        cx = x + i * step
        c.setFillColor(CARMINE)
        c.circle(cx, y_line, 3, stroke=0, fill=1)
        c.setFillColor(CARMINE_DARK)
        c.setFont("DVS-Bold", size + 1)
        c.drawCentredString(cx, y_line + 7, yr)
        c.setFillColor(INK)
        c.setFont("DVS", size - 1.5)
        for j, ln in enumerate(wrap(txt, step * 0.95, "DVS", size - 1.5)[:3]):
            c.drawCentredString(cx, y_line - 10 - j * (size - 0.5), ln)


def cover_bg(c):
    c.setFillColor(HexColor("#fbf7ef"))
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    c.setFillColor(CARMINE)
    c.rect(0, PAGE_H - 4 * mm, PAGE_W, 4 * mm, stroke=0, fill=1)
    c.rect(0, 0, PAGE_W, 4 * mm, stroke=0, fill=1)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.rect(M / 2, M / 2, PAGE_W - M, PAGE_H - M, stroke=1, fill=0)


def page1(c):
    header(c, "A Baltic nation on the eastern shore of the Baltic Sea", "Latvia — Land, People and Origins", 1)

    left_x = M
    right_x = PAGE_W - M - 116 * mm
    col_w = PAGE_W - 2 * M - 116 * mm - GUTTER
    y0 = CONTENT_TOP - 8 * mm

    y = section_label(c, left_x, y0, "The land")
    y = bullets(c, left_x, y, col_w, [
        ("", "Latvia (64,589 km²) lies on the Baltic Sea between Estonia and Lithuania. Its name comes from the ancient Baltic tribe of the Latgallians."),
        ("", "Rivers — above all the Daugava (1,020 km) — forests (about half the country) and a 531 km coastline have shaped life, trade and defence for a thousand years."),
        ("", "Amber from the Baltic coast, the \u201cgold of the North\u201d, linked Latvia to the Roman Empire and the Silk Road more than 2,000 years ago."),
    ])
    y = section_label(c, left_x, y - 2 * mm, "The people and the language")
    y = bullets(c, left_x, y, col_w, [
        ("", "Latvians speak Latvian, one of only two surviving Baltic languages (with Lithuanian) of the Indo-European family — a sister group to Slavic and Germanic."),
        ("", "The Latvian nation formed from Baltic tribes — Latgallians, Curonians, Semigallians — with Finnic Livonian neighbours."),
        ("", "Population today: about 1.9 million; the largest city is Riga (~605,000), founded in 1201."),
    ])

    hero_h = 62 * mm
    draw_image_box(c, os.path.join(ASSETS, "ai_riga_sunset.jpg"), right_x, y0, 116 * mm, hero_h,
                   caption="Riga, the capital, at sunset (illustration)")

    strip_top = CONTENT_BOTTOM + 52 * mm
    y = section_label(c, left_x, strip_top, "From ancient tribes to a modern state — the road in brief")
    timeline(c, left_x, y - 1 * mm, PAGE_W - 2 * M, [
        ("c. 3000 BC", "Baltic tribes arrive"),
        ("12th c.", "Crusaders found Riga (1201)"),
        ("1561", "Livonian Confederation ends"),
        ("1629–1710", "Swedish rule"),
        ("1710–1918", "Russian Empire"),
        ("1918", "Republic proclaimed 18 Nov"),
        ("1940–91", "Soviet occupation"),
        ("2004", "Joins EU and NATO"),
    ])
    img_top = y - 22 * mm
    img_h = 30 * mm
    iw = 66 * mm
    gap = 6 * mm
    x1 = left_x
    x2 = left_x + iw + gap
    x3 = PAGE_W - M - iw
    draw_image_box(c, os.path.join(ASSETS, "ai_ancient_balts.jpg"), x1, img_top, iw, img_h,
                   caption="Ancient Baltic hillforts (illustration)", caption_size=7)
    draw_image_box(c, os.path.join(ASSETS, "w_old_town.jpg"), x2, img_top, iw, img_h,
                   caption="Riga Old Town (photo: Diliff, CC BY-SA)", caption_size=7)
    draw_image_box(c, os.path.join(ASSETS, "w_bauska_castle.jpg"), x3, img_top, iw, img_h,
                   caption="Bauska Castle, 15th–16th c. (photo: Wikimedia Commons)", caption_size=7)
    footer(c, "Sources: Encyclopaedia Britannica; Latvian Institute; Wikimedia Commons (CC). Illustrations generated for this deck.")
    c.showPage()


def page2(c):
    header(c, "Empires, wars and the struggle for independence", "Centuries of Change: 13th–20th Century", 2)
    col_w = (PAGE_W - 2 * M - GUTTER) / 2
    x1 = M
    x2 = M + col_w + GUTTER
    y0 = CONTENT_TOP - 8 * mm

    y = section_label(c, x1, y0, "Medieval Livonia (1200s–1561)")
    y = bullets(c, x1, y, col_w, [
        ("", "The Livonian Brothers of the Sword bring Christianity; Riga is founded in 1201 and joins the Hanseatic League — one of northern Europe's great trading cities."),
        ("", "Teutonic Knights, bishops and Riga's merchants shape Terra Mariana (\u201cLand of Mary\u201d). Castles such as Cēsis, Turaida and Bauska rise across the land."),
        ("", "The Reformation (1520s–30s) makes Livonia Lutheran; the Livonian Confederation crumbles in the Livonian War (1558–1583)."),
    ], size=9.6, leading=12.6, gap=4)
    y = section_label(c, x1, y - 1 * mm, "Polish–Lithuanian and Swedish rule (1561–1721)")
    y = bullets(c, x1, y, col_w, [
        ("", "The Duchy of Courland (1561) becomes a thriving vassal of Poland–Lithuania, with a fleet that even colonised Tobago (1642)."),
        ("", "Under Sweden (1629–1710) Riga's trade booms; the Great Northern War (1700–1721) devastates the land and brings it under Russia."),
    ], size=9.6, leading=12.6, gap=4)
    y = section_label(c, x1, y - 1 * mm, "In the Russian Empire (1721–1918)")
    y = bullets(c, x1, y, col_w, [
        ("", "Serfdom abolished in Courland (1817) and Livonia (1819). The National Awakening (from the 1850s) revives language and song: the first Song Festival, Riga 1873."),
        ("", "Industrialisation and railways grow Riga into the Empire's third city; the 1905 Revolution is violently suppressed."),
        ("", "WWI brings front lines and 700,000 Latvian Riflemen; the Russian collapse opens the way to independence."),
    ], size=9.6, leading=12.6, gap=4)

    y = section_label(c, x2, y0, "Independence and occupation (1918–1991)")
    y = bullets(c, x2, y, col_w, [
        ("18 Nov 1918", "The Republic of Latvia is proclaimed in Riga; a war of independence (1918–1920) secures it against Soviet Russia and German forces."),
        ("", "The interwar republic flourishes — democracy, land reform, education — while caught between Nazi Germany and Stalin's USSR (Molotov–Ribbentrop Pact, 1939)."),
        ("1940–41, 1944–91", "Two Soviet occupations: the deportations of 14 June 1941 and 25 March 1949 send ~94,000 Latvians to Siberia; forced collectivisation and Russification follow."),
        ("", "Nazi German occupation (1941–44) brings the Holocaust: ~70,000 Latvian Jews are murdered."),
        ("1987–1991", "The Singing Revolution: the Baltic Way human chain of 23 Aug 1989 (2 million people, 600 km) restores independence, de facto on 21 Aug 1991."),
    ], size=9.6, leading=12.6, gap=4)

    img_top = CONTENT_BOTTOM + 34 * mm
    img_h = 26 * mm
    draw_image_box(c, os.path.join(ASSETS, "ai_medieval_livonia.jpg"), x1, img_top, col_w, img_h,
                   caption="Medieval Hanseatic Riga on the Daugava (illustration)", caption_size=7)
    half = (col_w - GUTTER / 2) / 2
    draw_image_box(c, os.path.join(ASSETS, "ai_1918_proclamation.jpg"), x2, img_top, half, img_h,
                   caption="Proclamation, 18 Nov 1918 (illustration)", caption_size=7)
    draw_image_box(c, os.path.join(ASSETS, "ai_baltic_way.jpg"), x2 + half + GUTTER / 2, img_top, half, img_h,
                   caption="The Baltic Way, 23 Aug 1989 (illustration)", caption_size=7)
    footer(c, "Sources: Encyclopaedia Britannica; Latvian History (Latvian Institute); USHMM. Illustrations generated for this deck.")
    c.showPage()


def page3(c):
    header(c, "A free nation in Europe — and the culture that kept it alive", "Independence Restored & Latvia Today", 3)
    col_w = (PAGE_W - 2 * M - GUTTER) / 2
    x1 = M
    x2 = M + col_w + GUTTER
    y0 = CONTENT_TOP - 8 * mm

    y = section_label(c, x1, y0, "Restored independence and today")
    y = bullets(c, x1, y, col_w, [
        ("1991–2004", "Independence restored (21 Aug 1991); Soviet troops leave by 1994; Latvia joins the EU and NATO in 2004 and the eurozone in 2014."),
        ("", "Today Latvia is a stable parliamentary republic of ~1.9 million people. Riga's Old Town is a UNESCO World Heritage site; the country leads in digital government."),
        ("", "Latvia stands with Ukraine: since 2022 it has hosted tens of thousands of refugees and is among Ukraine's strongest supporters."),
        ("", "Flag: carmine red (\u201cLatvian red\u201d) with a white stripe — one of the world's oldest flags, legend says born from a blood-stained battlefield banner."),
    ], size=9.8, leading=13, gap=4)
    y = section_label(c, x1, y - 1 * mm, "The Song and Dance Festival")
    y = bullets(c, x1, y, col_w, [
        ("", "First held in 1873, the Latvian Song and Dance Celebration gathers up to ~40,000 singers and dancers; listed by UNESCO in 2003 as Intangible Cultural Heritage."),
        ("", "Songs carried the nation through 50 years of occupation — singing was an act of quiet resistance."),
    ], size=9.8, leading=13, gap=4)

    right_img_h = 26 * mm
    right_gap = 9 * mm
    ytop = y0
    draw_image_box(c, os.path.join(ASSETS, "w_freedom_monument.jpg"), x2, ytop, col_w, right_img_h,
                   caption="Freedom Monument, Riga — \u201cMilda\u201d, 1935 (photo: Wikimedia Commons)", caption_size=7)
    draw_image_box(c, os.path.join(ASSETS, "ai_modern_riga.jpg"), x2, ytop - right_img_h - right_gap, col_w, right_img_h,
                   caption="Modern Riga at dusk (illustration)", caption_size=7)
    draw_image_box(c, os.path.join(ASSETS, "ai_deportations_1941.jpg"), x2, ytop - 2 * (right_img_h + right_gap), col_w, right_img_h,
                   caption="June 1941 deportations — remembered (illustration)", caption_size=7)

    bot_top = CONTENT_BOTTOM + 40 * mm
    bot_h = 32 * mm
    draw_image_box(c, os.path.join(ASSETS, "w_song_festival.jpg"), x1, bot_top, col_w, bot_h,
                   caption="Latvian Song and Dance Celebration 2023 (photo: Wikimedia Commons, CC)", caption_size=7)

    bx, by, bw, bh = x2, CONTENT_BOTTOM, col_w, bot_h
    c.setFillColor(CREAM)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    c.roundRect(bx, by, bw, bh, 5, stroke=1, fill=1)
    c.setFillColor(CARMINE_DARK)
    c.setFont("DVS-Bold", 10)
    c.drawString(bx + 5 * mm, by + bh - 7 * mm, "KEY FACTS")
    c.setFillColor(INK)
    c.setFont("DVS", 8.6)
    facts = [
        "Capital: Riga (founded 1201)  \u2022  Area: 64,589 km\u00b2  \u2022  Population: ~1.9 M",
        "Language: Latvian (Baltic, Indo-European)  \u2022  Currency: euro (\u20ac) since 2014",
        "Government: parliamentary republic  \u2022  EU & NATO member since 2004",
        "UNESCO: Historic Centre of Riga; Struve Geodetic Arc; Song Festival tradition",
    ]
    fy = by + bh - 13 * mm
    for f in facts:
        c.drawString(bx + 5 * mm, fy, f)
        fy -= 5.2 * mm
    footer(c, "Sources: Encyclopaedia Britannica; UNESCO; Latvian Ministry of Foreign Affairs; Wikimedia Commons (CC). Illustrations generated for this deck.")
    c.showPage()


def main():
    c = canvas.Canvas(OUT, pagesize=(PAGE_W, PAGE_H))
    c.setTitle("The History of Latvia — 3-page presentation")
    c.setAuthor("Vibe Code")
    c.setSubject("History of Latvia: origins, empires, independence and today")
    c.setCreator("ReportLab")
    for fn in (page1, page2, page3):
        cover_bg(c)
        fn(c)
    c.save()
    print("Wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
