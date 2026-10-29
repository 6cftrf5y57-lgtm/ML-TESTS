#!/usr/bin/env python3
"""3-page A4 landscape presentation PDF on the history of Latvia."""

import os
from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets")
FONTS = os.path.join(BASE, "fonts")
OUT = os.path.join(BASE, "History_of_Latvia.pdf")

PAGE_W, PAGE_H = landscape(A4)  # 841.89 x 595.28 pt

CARMINE = HexColor("#9E1B32")
CARMINE_DARK = HexColor("#7A1426")
WHITE = HexColor("#FFFFFF")
INK = HexColor("#241f20")
GOLD = HexColor("#C9A227")
CREAM = HexColor("#F7F2E9")
SLATE = HexColor("#3d4756")

pdfmetrics.registerFont(TTFont("DVS", os.path.join(FONTS, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DVS-Bold", os.path.join(FONTS, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DVS-Obl", os.path.join(FONTS, "DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFont(TTFont("DVSerif", os.path.join(FONTS, "DejaVuSerif.ttf")))
pdfmetrics.registerFont(TTFont("DVSerif-Bold", os.path.join(FONTS, "DejaVuSerif-Bold.ttf")))

M = 14 * mm  # page margin


def img_size(path, max_w, max_h):
    im = Image.open(path)
    w, h = im.size
    scale = min(max_w / w, max_h / h)
    return w * scale, h * scale, w, h


def draw_image_fit(c, path, x, y, max_w, max_h, frame=True, radius=0):
    w, h, pw, ph = img_size(path, max_w, max_h)
    dx = x + (max_w - w) / 2
    dy = y + (max_h - h) / 2
    if frame:
        c.setFillColor(WHITE)
        c.setStrokeColor(CARMINE)
        c.setLineWidth(1.2)
        c.roundRect(dx - 4, dy - 4, w + 8, h + 8, 6, stroke=1, fill=1)
    c.drawImage(ImageReader(path), dx, dy, w, h, preserveAspectRatio=True, mask="auto")
    return dx, dy, w, h


def flag_badge(c, x, y, w, h):
    """Latvian carmine-white-carmine flag."""
    c.saveState()
    c.setFillColor(CARMINE)
    c.rect(x, y + h * (1 - 0.4), w, h * 0.4, stroke=0, fill=1)
    c.rect(x, y, w, h * 0.4, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.rect(x, y + h * 0.4, w, h * 0.2, stroke=0, fill=1)
    c.setStrokeColor(HexColor("#d8cfc0"))
    c.setLineWidth(0.6)
    c.rect(x, y, w, h, stroke=1, fill=0)
    c.restoreState()


def header(c, kicker, title, page_no, total=3):
    c.setFillColor(CARMINE)
    c.rect(0, PAGE_H - 16 * mm, PAGE_W, 16 * mm, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.rect(0, PAGE_H - 17 * mm, PAGE_W, 1 * mm, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.setFont("DVS-Bold", 10.5)
    c.drawString(M, PAGE_H - 8.2 * mm, kicker.upper())
    c.setFont("DVSerif-Bold", 21)
    c.drawString(M, PAGE_H - 14.2 * mm, title)
    flag_badge(c, PAGE_W - M - 34, PAGE_H - 13.5 * mm, 34, 19)
    c.setFont("DVS", 9)
    c.setFillColor(HexColor("#f3dfe3"))
    c.drawRightString(PAGE_W - M - 42, PAGE_H - 9 * mm, f"{page_no} / {total}")


def footer(c, note):
    c.setFillColor(HexColor("#8a8a8a"))
    c.setFont("DVS", 7.5)
    c.drawString(M, 6.5 * mm, note)
    c.drawRightString(PAGE_W - M, 6.5 * mm, "The History of Latvia")


def section_label(c, x, y, text):
    c.setFillColor(CARMINE)
    c.setFont("DVS-Bold", 11)
    c.drawString(x, y, text.upper())
    w = pdfmetrics.stringWidth(text.upper(), "DVS-Bold", 11)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.6)
    c.line(x, y - 3, x + w, y - 3)


def bullets(c, x, y, width, items, size=10.5, leading=14.5, gap=5, color=INK, bullet_color=CARMINE):
    c.setFillColor(color)
    for head, body in items:
        c.setFillColor(bullet_color)
        c.setFont("DVS-Bold", size)
        c.drawString(x, y, "\u25a0")
        tx = x + 10
        c.setFillColor(color)
        if head:
            c.setFont("DVS-Bold", size)
            c.drawString(tx, y, head)
            hw = pdfmetrics.stringWidth(head + " ", "DVS-Bold", size)
            c.setFont("DVS", size)
            lines = wrap(body, width - 10 - hw, "DVS", size)
            first = lines[0] if lines else ""
            c.drawString(tx + hw, y, first)
            y -= leading
            for ln in lines[1:]:
                c.drawString(tx, y, ln)
                y -= leading
        else:
            c.setFont("DVS", size)
            lines = wrap(body, width - 10, "DVS", size)
            for ln in lines:
                c.drawString(tx, y, ln)
                y -= leading
        y -= gap
    return y


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


def timeline(c, x, y, width, events, size=9.5):
    """events: list of (year, text). Horizontal mini-timeline."""
    n = len(events)
    step = width / max(n - 1, 1)
    c.setStrokeColor(HexColor("#cbb98a"))
    c.setLineWidth(2)
    c.line(x, y, x + width, y)
    for i, (yr, txt) in enumerate(events):
        cx = x + i * step
        c.setFillColor(CARMINE)
        c.circle(cx, y, 3.2, stroke=0, fill=1)
        c.setFillColor(CARMINE_DARK)
        c.setFont("DVS-Bold", size + 1)
        c.drawCentredString(cx, y + 8, yr)
        c.setFillColor(INK)
        c.setFont("DVS", size - 1.5)
        for j, ln in enumerate(wrap(txt, step * 0.98, "DVS", size - 1.5)[:3]):
            c.drawCentredString(cx, y - 11 - j * (size - 1), ln)


def page1(c):
    header(c, "A Baltic nation on the eastern shore of the Baltic Sea", "Latvia — Land, People and Origins", 1)
    top = PAGE_H - 16 * mm
    # Hero image (right)
    hero_w = 118 * mm
    draw_image_fit(c, os.path.join(ASSETS, "ai_riga_sunset.jpg"), PAGE_W - M - hero_w, top - 78 * mm - 8, hero_w, 78 * mm)
    c.setFont("DVS-Obl", 8)
    c.setFillColor(HexColor("#777777"))
    c.drawRightString(PAGE_W - M, top - 78 * mm - 12, "Riga, the capital, at sunset (illustration)")

    left_w = PAGE_W - 2 * M - hero_w - 8 * mm
    x = M
    y = top - 10 * mm
    section_label(c, x, y, "The land")
    y -= 6 * mm
    y = bullets(c, x, y, left_w, [
        ("", "Latvia (64,589 km²) lies on the Baltic Sea between Estonia and Lithuania. Its name comes from the ancient Baltic tribe of the Latgallians."),
        ("", "Rivers — above all the Daugava (1,020 km) — forests (about half the country) and a 531 km coastline have shaped life, trade and defence for a thousand years."),
        ("", "Amber from the Baltic coast, the \u201cgold of the North\u201d, linked Latvia to the Roman Empire and the Silk Road more than 2,000 years ago."),
    ], size=10.5, leading=14, gap=4)
    y -= 2 * mm
    section_label(c, x, y, "The people and the language")
    y -= 6 * mm
    y = bullets(c, x, y, left_w, [
        ("", "Latvians speak Latvian, one of only two surviving Baltic languages (with Lithuanian) of the Indo-European family — a sister group to Slavic and Germanic."),
        ("", "The ethnic Latvian nation formed from Baltic tribes — Latgallians, Curonians, Semigallians and Livonians/Livs — with Finnic Livonian and Selonian neighbours."),
        ("", "Population today: about 1.9 million; the largest city is Riga (~605,000), founded in 1201."),
    ], size=10.5, leading=14, gap=4)

    # Bottom strip: ancient + medieval images and timeline
    bot_y = 12 * mm
    strip_h = 62 * mm
    section_label(c, x, bot_y + strip_h + 6, "From ancient tribes to a modern state — the road in brief")
    tl_y = bot_y + strip_h + 2
    timeline(c, x, tl_y, PAGE_W - 2 * M, [
        ("c. 3000 BC", "Baltic tribes arrive; Corded Ware culture"),
        ("12th c.", "German crusaders found Riga (1201)"),
        ("1561", "Livonian Confederation dissolves"),
        ("1621–1710", "Swedish rule; Riga grows"),
        ("1710–1918", "Russian Empire"),
        ("1918", "Republic proclaimed 18 Nov"),
        ("1940–91", "Soviet occupation; restored 1991"),
        ("2004", "Joins EU and NATO"),
    ])
    # two small images at bottom-left
    iw = 62 * mm
    ih = 40 * mm
    draw_image_fit(c, os.path.join(ASSETS, "ai_ancient_balts.jpg"), x, bot_y, iw, ih)
    draw_image_fit(c, os.path.join(ASSETS, "w_old_town.jpg"), x + iw + 6 * mm, bot_y, iw, ih)
    c.setFont("DVS-Obl", 7.5)
    c.setFillColor(HexColor("#777777"))
    c.drawString(x, bot_y - 4.5 * mm, "Ancient Baltic hillforts and amber trade (illustration)")
    c.drawString(x + iw + 6 * mm, bot_y - 4.5 * mm, "Riga Old Town: House of the Blackheads & St. Peter's (photo: Diliff, CC BY-SA)")
    # right bottom image
    draw_image_fit(c, os.path.join(ASSETS, "w_bauska_castle.jpg"), PAGE_W - M - iw, bot_y, iw, ih)
    c.setFont("DVS-Obl", 7.5)
    c.setFillColor(HexColor("#777777"))
    c.drawRightString(PAGE_W - M, bot_y - 4.5 * mm, "Bauska Castle, 15th–16th c. Renaissance residence (photo: Wikimedia Commons)")
    footer(c, "Sources: Encyclopaedia Britannica; Latvian Institute; Wikimedia Commons (CC). Illustrations generated for this deck.")
    c.showPage()


def page2(c):
    header(c, "Empires, wars and the struggle for independence", "Centuries of Change: 13th–20th Century", 2)
    top = PAGE_H - 16 * mm
    col_w = (PAGE_W - 2 * M - 10 * mm) / 2
    x1 = M
    x2 = M + col_w + 10 * mm

    # Left column
    y = top - 8 * mm
    section_label(c, x1, y, "Medieval Livonia (1200s–1561)")
    y -= 6 * mm
    y = bullets(c, x1, y, col_w, [
        ("", "The Livonian Brothers of the Sword bring Christianity; Riga is founded in 1201 and joins the Hanseatic League — one of northern Europe's great trading cities."),
        ("", "Teutonic Knights, bishops and Riga's merchants shape Terra Mariana (\u201cLand of Mary\u201d). Castles such as Cēsis, Turaida and Bauska rise across the land."),
        ("", "Reformation (1520s–30s) makes Livonia Lutheran; the Livonian Confederation crumbles in the Livonian War (1558–1583)."),
    ], size=9.8, leading=13, gap=4)
    y -= 1 * mm
    section_label(c, x1, y, "Polish–Lithuanian and Swedish rule (1561–1721)")
    y -= 6 * mm
    y = bullets(c, x1, y, col_w, [
        ("", "The Duchy of Courland (1561) becomes a thriving vassal of Poland–Lithuania with a fleet that even colonised Tobago (1642)."),
        ("", "Under Sweden (Vidzeme, 1629–1710) Riga's trade booms; the Great Northern War (1700–1721) devastates the land and brings it under Russia."),
    ], size=9.8, leading=13, gap=4)
    y -= 1 * mm
    section_label(c, x1, y, "In the Russian Empire (1721–1918)")
    y -= 6 * mm
    y = bullets(c, x1, y, col_w, [
        ("", "Serfdom is abolished in Courland (1817) and Livonia (1819). The Latvian National Awakening (from the 1850s) revives language and song: the first Song Festival, Riga 1873."),
        ("", "Industrialisation and railways grow Riga into the Empire's third city; the 1905 Revolution is violently suppressed."),
        ("", "WWI brings front lines and 700,000 Latvian Riflemen; the Russian collapse opens the way to independence."),
    ], size=9.8, leading=13, gap=4)
    img_h = 46 * mm
    draw_image_fit(c, os.path.join(ASSETS, "ai_medieval_livonia.jpg"), x1, 12 * mm, col_w, img_h)
    c.setFont("DVS-Obl", 7.5)
    c.setFillColor(HexColor("#777777"))
    c.drawString(x1, 12 * mm - 4.5 * mm, "Medieval Hanseatic Riga on the Daugava (illustration)")

    # Right column
    y = top - 8 * mm
    section_label(c, x2, y, "Independence and occupation (1918–1991)")
    y -= 6 * mm
    y = bullets(c, x2, y, col_w, [
        ("18 Nov 1918", "The Republic of Latvia is proclaimed in Riga; a war of independence (1918–1920) secures it against Soviet Russia and German forces."),
        ("", "The interwar republic flourishes — democracy, land reform, education — while caught between Nazi Germany and Stalin's USSR (Molotov–Ribbentrop Pact, 1939)."),
        ("1940–1941, 1944–1991", "Two Soviet occupations: mass deportations of 14 June 1941 and 25 March 1949 send ~94,000 Latvians to Siberia; forced collectivisation and Russification follow."),
        ("", "Nazi German occupation (1941–44) brings the Holocaust: ~70,000 Latvian Jews are murdered."),
        ("1987–1991", "The Singing Revolution: the Baltic Way human chain of 23 Aug 1989 (2 million people, 600 km) and mass demonstrations restore independence on 4 May 1990; de facto restored 21 Aug 1991."),
    ], size=9.8, leading=13, gap=4)
    # two stacked images right
    ih2 = 22.5 * mm
    draw_image_fit(c, os.path.join(ASSETS, "ai_1918_proclamation.jpg"), x2, 12 * mm + ih2 + 5 * mm, col_w, ih2)
    draw_image_fit(c, os.path.join(ASSETS, "ai_baltic_way.jpg"), x2, 12 * mm, col_w, ih2)
    c.setFont("DVS-Obl", 7.5)
    c.setFillColor(HexColor("#777777"))
    c.drawString(x2, 12 * mm + ih2 + 5 * mm + ih2 + 2.5 * mm, "Proclamation of the Republic, 18 November 1918 (illustration)")
    c.drawString(x2, 12 * mm - 4.5 * mm, "The Baltic Way, 23 August 1989 (illustration)")
    footer(c, "Sources: Encyclopaedia Britannica; Latvian History (Latvian Institute, 2005); USHMM. Illustrations generated for this deck.")
    c.showPage()


def page3(c):
    header(c, "A free nation in Europe — and the culture that kept it alive", "Independence Restored & Latvia Today", 3)
    top = PAGE_H - 16 * mm
    col_w = (PAGE_W - 2 * M - 10 * mm) / 2
    x1 = M
    x2 = M + col_w + 10 * mm

    y = top - 8 * mm
    section_label(c, x1, y, "Restored independence and today")
    y -= 6 * mm
    y = bullets(c, x1, y, col_w, [
        ("1991–2004", "Independence restored (21 Aug 1991); Soviet troops leave by 1994; Latvia joins the EU and NATO in 2004 and the eurozone in 2014."),
        ("", "Today Latvia is a stable parliamentary republic of ~1.9 million people. Riga's Old Town is a UNESCO World Heritage site; the country leads in digital government (e-residency)."),
        ("", "Latvia stands with Ukraine: since 2022 it has hosted tens of thousands of refugees and is among the strongest supporters of Ukraine's EU and NATO membership."),
        ("", "Flag: carmine red (\u201cLatvian red\u201d) with a white stripe — one of the world's oldest flags, legend says born from a blood-stained battlefield banner."),
    ], size=10, leading=13.5, gap=4)
    y -= 1 * mm
    section_label(c, x1, y, "The Song and Dance Festival — the heartbeat of the nation")
    y -= 6 * mm
    y = bullets(c, x1, y, col_w, [
        ("", "First held in 1873, the Latvian Song and Dance Celebration gathers up to ~40,000 singers and dancers; it was listed by UNESCO in 2003 as a Masterpiece of Oral and Intangible Heritage."),
        ("", "Songs carried the nation through 50 years of occupation — singing was an act of quiet resistance."),
    ], size=10, leading=13.5, gap=4)
    ih = 44 * mm
    draw_image_fit(c, os.path.join(ASSETS, "w_song_festival.jpg"), x1, 12 * mm, col_w, ih)
    c.setFont("DVS-Obl", 7.5)
    c.setFillColor(HexColor("#777777"))
    c.drawString(x1, 12 * mm - 4.5 * mm, "Latvian Song and Dance Celebration 2023 (photo: Wikimedia Commons, CC)")

    # Right column: images + key facts
    y = top - 8 * mm
    section_label(c, x2, y, "Latvia in pictures")
    y -= 6 * mm
    gap = 5 * mm
    ih2 = (top - 8 * mm - 6 * mm - 12 * mm - 46 * mm - 3 * gap) / 2
    rows = [
        ("w_freedom_monument.jpg", "Freedom Monument, Riga — \u201cMilda\u201d, unveiled 1935 (photo: Wikimedia Commons)"),
        ("ai_modern_riga.jpg", "Modern Riga at dusk (illustration)"),
    ]
    yy = y
    for img, cap in rows:
        draw_image_fit(c, os.path.join(ASSETS, img), x2, yy - ih2, col_w, ih2)
        c.setFont("DVS-Obl", 7.5)
        c.setFillColor(HexColor("#777777"))
        c.drawString(x2, yy - ih2 - 4 * mm, cap)
        yy = yy - ih2 - 8 * mm
    draw_image_fit(c, os.path.join(ASSETS, "ai_deportations_1941.jpg"), x2, yy - ih2, col_w, ih2)
    c.setFont("DVS-Obl", 7.5)
    c.setFillColor(HexColor("#777777"))
    c.drawString(x2, yy - ih2 - 4 * mm, "June 1941 deportations — remembered, never forgotten (illustration)")

    # Key facts band bottom-right
    facts_y = 12 * mm
    c.setFillColor(CREAM)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    bw = col_w
    bh = 30 * mm
    c.roundRect(x2, facts_y, bw, bh, 5, stroke=1, fill=1)
    c.setFillColor(CARMINE_DARK)
    c.setFont("DVS-Bold", 10)
    c.drawString(x2 + 5 * mm, facts_y + bh - 7 * mm, "KEY FACTS")
    c.setFillColor(INK)
    c.setFont("DVS", 8.8)
    facts = [
        "Capital: Riga (founded 1201)  \u2022  Area: 64,589 km\u00b2  \u2022  Population: ~1.9 M",
        "Language: Latvian (Baltic branch of Indo-European)  \u2022  Currency: euro (\u20ac) since 2014",
        "Government: parliamentary republic  \u2022  EU & NATO member since 2004",
        "UNESCO sites: Historic Centre of Riga; Struve Geodetic Arc; Song Festival tradition",
    ]
    fy = facts_y + bh - 13 * mm
    for f in facts:
        c.drawString(x2 + 5 * mm, fy, f)
        fy -= 5.4 * mm
    footer(c, "Sources: Encyclopaedia Britannica; UNESCO; Latvian Ministry of Foreign Affairs; Wikimedia Commons (CC). Illustrations generated for this deck.")
    c.showPage()


def cover_bg(c):
    c.setFillColor(HexColor("#fbf7ef"))
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    c.setFillColor(CARMINE)
    c.rect(0, PAGE_H - 5 * mm, PAGE_W, 5 * mm, stroke=0, fill=1)
    c.rect(0, 0, PAGE_W, 5 * mm, stroke=0, fill=1)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.4)
    c.rect(M, M, PAGE_W - 2 * M, PAGE_H - 2 * M, stroke=1, fill=0)


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
