#!/usr/bin/env python3
"""Erzeugt die komplette Seite netzautos.at als statische HTML-Dateien.

Aufruf (im Ordner _quelle):  python3 build.py
Schreibt direkt in die Repository-Wurzel: Startseite, Rechner, Ratgeber, Rechtliches, sitemap.xml, llms.txt.
"""
import html, json, re, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "_quelle" / "ratgeber"
SITE = "https://netzautos.at"
NAME = "netzautos"
STAND = "2026-11-09"

# Reihenfolge = Reihenfolge auf der Übersicht
ARTIKEL = [
    dict(handle="e-auto-foerderung-oesterreich",
         h1="E-Auto-Förderung Österreich 2026: Was es noch gibt",
         seo="E-Auto-Förderung Österreich 2026: Was bleibt | netzautos",
         desc="Keine Bundesprämie mehr: Was 2026 für E-Autos in Österreich noch gefördert wird, Burgenland mit 2.000 €, NoVA-Befreiung und was für Gebrauchte gilt.",
         kurz="Bund, Bundesländer, NoVA und was das für den Gebrauchtkauf bedeutet.",
         thema="Förderung", published=STAND, modified=STAND),
    dict(handle="wallbox-kosten-foerderung",
         h1="Wallbox in Österreich: Kosten, Förderung 2026, Anmeldung",
         seo="Wallbox Österreich: Förderung 2026 & Anmeldung | netzautos",
         desc="Wallbox-Förderung 2026 nach Bundesland (Burgenland, Steiermark), Meldepflicht beim Netzbetreiber ab 3,68 kVA und was die Installation teurer macht.",
         kurz="Förderung nach Bundesland, Meldepflicht und die wichtigsten Kostentreiber.",
         thema="Laden", published=STAND, modified=STAND),
]

AUTOR = {"@type": "Person", "name": "Anton Scharmitzer", "honorificPrefix": "Mag.",
         "jobTitle": "Herausgeber, Betriebswirt", "url": f"{SITE}/impressum/"}
ORG = {"@type": "Organization", "@id": f"{SITE}/#organization", "name": "netzautos", "url": f"{SITE}/",
       "logo": f"{SITE}/icon.svg", "description": "Unabhängiger Ratgeber für den Kauf gebrauchter Elektroautos in Österreich.",
       "areaServed": {"@type": "Country", "name": "Österreich"}}
WEBSITE = {"@type": "WebSite", "@id": f"{SITE}/#website", "url": f"{SITE}/", "name": "netzautos",
           "inLanguage": "de-AT", "publisher": {"@id": f"{SITE}/#organization"}}

LOGO = ('<svg width="34" height="34" viewBox="0 0 34 34" aria-hidden="true"><rect width="34" height="34" rx="9" fill="var(--accent)"/>'
        '<path d="M8 17l9-7 9 7M11 15.5V25h12v-9.5M15 25v-5h4v5" fill="none" stroke="var(--accent-ink)" stroke-width="2.2" '
        'stroke-linecap="round" stroke-linejoin="round"/></svg>')

def header(current=""):
    def a(href, text):
        cur = ' aria-current="page"' if href == current else ""
        return f'<a href="{href}"{cur}>{text}</a>'
    return ('<header class="site"><div class="w">'
            f'<a class="logo" href="/">{LOGO}<span>netzautos<span style="color:var(--accent)">.at</span></span></a>'
            '<nav class="main" aria-label="Hauptnavigation">'
            + a("/ratgeber/", "Ratgeber") + a("/foerder-check/", "Förder-Check") + a("/#fragen", "Häufige Fragen")
            + '</nav></div></header>')

FOOTER = ('<footer class="site"><div class="w"><p>netzautos.at bietet allgemeine Informationen rund um gebrauchte Elektroautos, Förderungen und Laden in Österreich. '
          'Die Inhalte ersetzen keine Rechts- oder Steuerberatung. © 2026 netzautos.at</p>'
          '<nav aria-label="Fußzeile"><a href="/ratgeber/">Ratgeber</a><a href="/foerder-check/">Förder-Check</a>'
          '<a href="/impressum/">Impressum</a><a href="/datenschutz/">Datenschutz</a></nav>'
          '</div></footer>')

def head(title, desc, url, ogtype, graph, robots="index, follow, max-snippet:-1, max-image-preview:large", extra=""):
    ld = ""
    if graph:
        ld = ('<script type="application/ld+json">\n'
              + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + "\n</script>")
    return f"""<!doctype html>
<html lang="de-AT">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#1D4ED8">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="preload" href="/fonts/pjs.woff2" as="font" type="font/woff2" crossorigin>
<meta property="og:type" content="{ogtype}">
<meta property="og:locale" content="de_AT">
<meta property="og:site_name" content="netzautos">
<meta property="og:title" content="{html.escape(title.replace(' | netzautos', ''))}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="/styles.css">
{extra}{ld}
</head>"""

def seite(title, desc, path, graph, body, current="", ogtype="website", robots=None, extra=""):
    url = SITE + path
    kw = {} if robots is None else {"robots": robots}
    return head(title, desc, url, ogtype, graph, extra=extra, **kw) + f"""
<body>
{header(current)}
<main>
{body}
</main>
{FOOTER}
</body>
</html>
"""

def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()

def faq_aus(body):
    teil = body.split("<h2>Häufige Fragen</h2>", 1)
    if len(teil) < 2:
        raise SystemExit("FAQ-Abschnitt fehlt")
    faq_html = teil[1].split("<h2", 1)[0]
    paare = re.findall(r"<h3>(.*?)</h3>\s*<p>(.*?)</p>", faq_html, re.S)
    if not 3 <= len(paare) <= 6:
        raise SystemExit(f"FAQ braucht 3–6 Fragen, gefunden {len(paare)}")
    return [(strip_tags(q), strip_tags(a)) for q, a in paare]

def toc_aus(body):
    eintraege, n = [], 0
    def ersetze(m):
        nonlocal n
        attrs, text = m.group(1), m.group(2)
        if 'id="' in attrs:
            hid = re.search(r'id="([^"]+)"', attrs).group(1)
        else:
            n += 1
            hid = "a" + str(n)
            attrs = f' id="{hid}"' + attrs
        if strip_tags(text) not in ("Quellen",):
            eintraege.append((hid, strip_tags(text)))
        return f"<h2{attrs}>{text}</h2>"
    body = re.sub(r"<h2([^>]*)>(.*?)</h2>", ersetze, body)
    return body, eintraege

def datum(iso):
    d = datetime.date.fromisoformat(iso)
    monate = ["Jänner", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
    return f"{d.day}. {monate[d.month-1]} {d.year}"

def crumbs(*teile):
    out = ['<a href="/">Startseite</a>']
    for href, text in teile:
        out.append(f'<a href="{href}">{text}</a>' if href else text)
    return '<nav class="crumbs" aria-label="Brotkrumen">' + " › ".join(out) + "</nav>"

def breadcrumb_ld(*teile):
    items = [{"@type": "ListItem", "position": 1, "name": "Startseite", "item": f"{SITE}/"}]
    for i, (name, path) in enumerate(teile, start=2):
        items.append({"@type": "ListItem", "position": i, "name": name, "item": SITE + path})
    return {"@type": "BreadcrumbList", "itemListElement": items}

# ---------- Ratgeber ----------

def artikel_seite(a, alle):
    path = f"/ratgeber/{a['handle']}/"
    url = SITE + path
    body = (SRC / f"{a['handle']}.html").read_text(encoding="utf-8")
    faqs = faq_aus(body)
    body, toc = toc_aus(body)
    erster = strip_tags(re.search(r"<p>(.*?)</p>", body, re.S).group(1)).replace("Die kurze Antwort:", "").strip()
    kurz_titel = a["h1"].split(":")[0]
    graph = [
        {"@type": "Article", "@id": url + "#article", "headline": a["h1"], "description": a["desc"],
         "inLanguage": "de-AT", "datePublished": a["published"], "dateModified": a["modified"],
         "author": AUTOR, "publisher": {"@id": f"{SITE}/#organization"},
         "mainEntityOfPage": url, "image": f"{SITE}/og.png", "abstract": erster,
         "about": {"@type": "Thing", "name": kurz_titel},
         "spatialCoverage": {"@type": "Country", "name": "Österreich"}},
        ORG,
        breadcrumb_ld(("Ratgeber", "/ratgeber/"), (kurz_titel, path)),
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in faqs]},
    ]
    toc_html = "".join(f'<li><a href="#{i}">{html.escape(t)}</a></li>' for i, t in toc)
    weitere = "".join(
        f'<li><a href="/ratgeber/{b["handle"]}/">{html.escape(b["h1"])}</a><span>{html.escape(b["kurz"])}</span></li>'
        for b in alle if b["handle"] != a["handle"])
    inhalt = f"""<div class="w narrow art">
{crumbs(("/ratgeber/", "Ratgeber"))}
<p class="eyebrow">Ratgeber · {html.escape(a['thema'])}</p>
<h1>{html.escape(a['h1'])}</h1>
<p class="meta">Geprüft am {datum(a['modified'])} · Von Mag. Anton Scharmitzer</p>
<details class="toc"><summary>Inhalt</summary><ol>{toc_html}</ol></details>
<div class="prose">
{body}
<div class="autor"><p><strong>Über diesen Ratgeber:</strong> Herausgegeben von Mag. Anton Scharmitzer, Betriebswirt (Studium der Internationalen Betriebswirtschaft an der Universität Wien). Alle Zahlen, Fristen und Förderbedingungen sind an den verlinkten Quellen mit Stand-Datum geprüft. Förderungen ändern sich oft: Prüfen Sie vor dem Kauf die aktuelle Richtlinie Ihres Bundeslandes.</p></div>
</div>
<aside class="tools-box"><p class="eyebrow">Kostenloses Werkzeug</p><div class="row"><a class="btn primary" href="/foerder-check/">Förder-Check für Ihr Bundesland</a></div></aside>
<section class="weiter"><h2>Weitere Ratgeber</h2><ul>{weitere}</ul></section>
</div>"""
    return seite(a["seo"], a["desc"], path, graph, inhalt, current="/ratgeber/", ogtype="article")

def uebersicht(alle):
    path = "/ratgeber/"
    graph = [
        {"@type": "CollectionPage", "@id": SITE + path, "url": SITE + path, "name": "Ratgeber gebrauchtes E-Auto in Österreich",
         "inLanguage": "de-AT", "isPartOf": {"@id": f"{SITE}/#website"},
         "hasPart": [{"@type": "Article", "headline": a["h1"], "url": f"{SITE}/ratgeber/{a['handle']}/"} for a in alle]},
        breadcrumb_ld(("Ratgeber", path)),
    ]
    karten = "".join(
        f'<a class="card rg" href="/ratgeber/{a["handle"]}/"><p class="num">{html.escape(a["thema"])}</p>'
        f'<h2>{html.escape(a["h1"])}</h2><p>{html.escape(a["kurz"])}</p></a>' for a in alle)
    inhalt = f"""<div class="w pad-s">
{crumbs((None, "Ratgeber"))}
<p class="eyebrow">Ratgeber</p>
<h1>Gebrauchtes E-Auto in Österreich</h1>
<p class="lead">Jede Antwort steht im ersten Absatz, jede Zahl ist an der Quelle geprüft und mit Stand-Datum versehen. Nur österreichische Regeln.</p>
<div class="grid4">{karten}</div>
<p style="margin:24px 0 0;font-size:14px;color:var(--muted)">Modell-Ratgeber (Zoe, Leaf, Model 3, ID.3, e-tron) und die Kauf-Checkliste erscheinen laufend.</p>
</div>"""
    return seite("Ratgeber E-Auto gebraucht kaufen | netzautos",
                 "Ratgeber für gebrauchte Elektroautos in Österreich: Förderung 2026, Wallbox, Laden daheim. Mit Quellen und Stand-Datum.",
                 path, graph, inhalt, current="/ratgeber/")

# ---------- Startseite ----------

FAQ_START = [
    ("Gibt es 2026 eine E-Auto-Förderung in Österreich?",
     "Vom Bund nicht mehr. Für Privatpersonen fördert 2026 nur das Burgenland den Kauf eines neuen E-Autos: 10 % des Preises, höchstens 2.000 €, bei einem Anschaffungspreis bis 50.000 €."),
    ("Wird ein gebrauchtes E-Auto gefördert?",
     "Nein. Die einzige Kaufförderung für Privatpersonen 2026 gilt laut Infoblatt des Landes Burgenland für Neuanschaffungen."),
    ("Muss ich für ein gebrauchtes E-Auto NoVA zahlen?",
     "Nein. E-Autos sind wegen null Gramm CO₂-Ausstoß von der Normverbrauchsabgabe befreit, auch wenn Sie ein gebrauchtes E-Auto aus dem Ausland importieren."),
    ("Wird die Wallbox gefördert?",
     "Im Einfamilienhaus nur noch im Burgenland und in der Steiermark, jeweils mit 30 % der Kosten, höchstens 300 €. Die Bundesförderung ist am 31. März 2026 ausgelaufen."),
    ("Muss ich eine Wallbox anmelden?",
     "Ja, Ladestationen über 3,68 kVA sind beim Netzbetreiber meldepflichtig. Das betrifft praktisch jede 11- oder 22-kW-Wallbox; meist übernimmt der Elektriker die Meldung."),
]

def startseite():
    graph = [ORG, WEBSITE,
             {"@type": "WebPage", "@id": f"{SITE}/#webpage", "url": f"{SITE}/", "name": "Gebrauchtes E-Auto kaufen in Österreich",
              "inLanguage": "de-AT", "isPartOf": {"@id": f"{SITE}/#website"}, "dateModified": STAND,
              "mainEntity": {"@id": f"{SITE}/#faq"}},
             {"@type": "FAQPage", "@id": f"{SITE}/#faq", "inLanguage": "de-AT", "mainEntity": [
                 {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ_START]}]
    faq_html = "".join(
        f'<details class="faq"{" open" if i == 0 else ""}><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>'
        for i, (q, a) in enumerate(FAQ_START))
    karten = "".join(
        f'<a class="card rg" href="/ratgeber/{a["handle"]}/"><p class="num">{html.escape(a["thema"])}</p>'
        f'<h2>{html.escape(a["h1"])}</h2><p>{html.escape(a["kurz"])}</p></a>' for a in ARTIKEL)
    laender = "".join(f'<a class="choice" href="/foerder-check/#{k}"><span><strong>{n}</strong></span><span aria-hidden="true">›</span></a>'
                      for k, n in [("bgld", "Burgenland"), ("stmk", "Steiermark"), ("wien", "Wien"), ("noe", "Niederösterreich")])
    inhalt = f"""<section class="hero"><div class="w">
<div class="text">
<p class="eyebrow">E-Auto gebraucht kaufen in Österreich</p>
<h1>Gebrauchtes E-Auto kaufen. Mit klarem Kopf.</h1>
<p class="lead">Was Sie über Förderung, Steuer, Akku und Laden daheim wissen müssen, bevor Sie unterschreiben. Nur österreichische Regeln, mit Quellen und Prüfdatum.</p>
<div class="row"><a class="btn primary" href="/foerder-check/">Förder-Check starten</a><a class="btn ghost" href="/ratgeber/">Zu den Ratgebern</a></div>
<div class="ticks"><span>✓ Alle 9 Bundesländer</span><span>✓ Quellen bei jeder Antwort</span><span>✓ Stand: November 2026</span></div>
</div>
<div class="panel">
<p class="eyebrow" style="margin-bottom:6px">Förder-Check</p>
<h2>Was gibt es in Ihrem Bundesland?</h2>
<div style="display:flex;flex-direction:column;gap:10px">{laender}
<a class="choice" href="/foerder-check/"><span><strong>Alle Bundesländer</strong><small>Kauf, Wallbox, bundesweite Vorteile</small></span><span aria-hidden="true">›</span></a>
</div>
</div>
</div></section>

<section class="stats" aria-label="Kernfakten 2026"><div class="w">
<div><p class="n">0 €</p><p>Kaufprämie vom Bund 2026</p></div>
<div><p class="n">0 € NoVA</p><p>für E-Autos, auch beim Import</p></div>
<div><p class="n">2 von 9</p><p>Bundesländern fördern die Wallbox</p></div>
<p style="flex:1 1 220px">Quellen: Land Burgenland, Land Steiermark, ÖAMTC. <a href="/ratgeber/e-auto-foerderung-oesterreich/">Alle Details</a></p>
</div></section>

<section id="schritte"><div class="w pad">
<p class="eyebrow">In drei Schritten</p>
<h2 class="h2">Vom Inserat bis zum ersten Laden daheim</h2>
<p class="lead">Die drei Fragen, die beim Gebrauchtkauf eines E-Autos wirklich zählen.</p>
<div class="grid4">
<article class="card phase"><p class="num">Schritt 1</p><h3>Modell und Akku prüfen</h3><p>Akkuzustand, Reichweite im Winter, Kaufakku oder Batteriemiete.</p><ul><li>Kauf-Checkliste für gebrauchte E-Autos (in Arbeit)</li><li>Modell-Ratgeber: Zoe, Leaf, Model 3, ID.3, e-tron (in Arbeit)</li></ul></article>
<article class="card phase"><p class="num">Schritt 2</p><h3>Förderung und Steuer klären</h3><p>Was Bund und Land 2026 noch zahlen und welche Abgaben anfallen.</p><ul><li><a href="/ratgeber/e-auto-foerderung-oesterreich/">E-Auto-Förderung 2026</a></li><li><a href="/foerder-check/">Förder-Check nach Bundesland</a></li></ul></article>
<article class="card phase"><p class="num">Schritt 3</p><h3>Daheim laden</h3><p>Steckdose oder Wallbox, Meldung beim Netzbetreiber, Förderung.</p><ul><li><a href="/ratgeber/wallbox-kosten-foerderung/">Wallbox: Kosten, Förderung, Anmeldung</a></li><li><a href="/ratgeber/wallbox-kosten-foerderung/#a4">Reicht die Haushaltssteckdose?</a></li></ul></article>
</div>
</div></section>

<section><div class="w pad-s">
<p class="eyebrow">Neueste Ratgeber</p>
<h2 class="h2" style="margin-bottom:28px">Gründlich statt oberflächlich</h2>
<div class="grid4">{karten}</div>
</div></section>

<section id="fragen" aria-labelledby="faq-titel"><div class="w narrow pad">
<p class="eyebrow">Häufige Fragen</p>
<h2 id="faq-titel" class="h2" style="margin-bottom:32px">E-Auto in Österreich: die wichtigsten Antworten</h2>
<div style="display:flex;flex-direction:column;gap:12px">{faq_html}</div>
<p style="margin:16px 0 0;font-size:14px;color:var(--muted)">Quellen: Land Burgenland, Land Steiermark, ÖAMTC, Netz NÖ. Details und Links in den <a href="/ratgeber/">Ratgebern</a>. Zuletzt geprüft: November 2026.</p>
</div></section>"""
    return seite("Gebrauchtes E-Auto kaufen Österreich | netzautos",
                 "Gebrauchtes E-Auto kaufen in Österreich: Förderung 2026 nach Bundesland, NoVA, Wallbox und Laden daheim. Mit gratis Förder-Check.",
                 "/", graph, inhalt, current="/")

# ---------- Förder-Check ----------

RECHNER_JS = r"""
<script>
(function(){
  'use strict';
  var KEINE = 'Keine Landesförderung für Privatpersonen.';
  var D = {
    bgld:{n:'Burgenland', kauf:'Neues E-Auto (Klasse M1): 10 % des Anschaffungspreises, höchstens 2.000 €, Preis bis 50.000 €. Antrag binnen sechs Monaten ab Rechnungsdatum, gilt für Rechnungen 2026, kein Rechtsanspruch. Gebrauchte E-Autos: laut Infoblatt nicht gefördert.',
          wb:'30 % der Kosten für Wallbox, Standsäule oder intelligentes Ladekabel, höchstens 300 €. Antrag binnen sechs Monaten ab Rechnungsdatum.',
          q:'https://www.burgenland.at/fileadmin/user_upload/Downloads/Wohnbaufoerderung/2026/Infoblaetter/E-Mobilitaet-2026.pdf', qt:'Infoblatt E-Mobilität 2026, Land Burgenland'},
    stmk:{n:'Steiermark', kauf:'Keine Kaufförderung für Privatpersonen.',
          wb:'30 % der Kosten, höchstens 300 €. Voraussetzungen: dreiphasige, intelligente Wallbox ab 11 kW; reines E-Auto auf Sie in der Steiermark zugelassen und privat genutzt; 100 % Ökostrom oder PV ab 1,5 kWp; Installation durch befugtes Elektrounternehmen; mindestens 7 Jahre Betrieb; Antrag binnen sechs Monaten.',
          q:'https://www.wohnbau.steiermark.at/cms/dokumente/12856318_165238372/66e011b0/2026_Infoblatt%20Intelligente%20E-Ladestationen.pdf', qt:'Infoblatt Intelligente E-Ladestationen 2026, Land Steiermark'},
    vbg:{n:'Vorarlberg', kauf:'Keine Kaufförderung für Privatpersonen.',
          wb:'Einfamilienhaus: keine Förderung. Mehrparteienhaus: 300 € je erschlossenem Stellplatz, höchstens 10.000 € je Gebäude (gefördert wird die Leitungsinfrastruktur).',
          q:'https://www.oeamtc.at/thema/elektromobilitaet/e-mobilitaetsfoerderungen-in-den-bundeslaendern-74006914', qt:'ÖAMTC, Stand 9. November 2026'},
    ooe:{n:'Oberösterreich', kauf:'Keine Kaufförderung für Privatpersonen.', wb:'Keine Förderung für die Wallbox im Einfamilienhaus. Für Mehrparteienhäuser beim Land Oberösterreich nachfragen.',
          q:'https://www.oeamtc.at/thema/elektromobilitaet/e-mobilitaetsfoerderungen-in-den-bundeslaendern-74006914', qt:'ÖAMTC, Stand 9. November 2026'},
    tirol:{n:'Tirol', kauf:'Keine Kaufförderung für Privatpersonen.', wb:'Keine Förderung für die private Wallbox.',
          q:'https://www.oeamtc.at/thema/elektromobilitaet/e-mobilitaetsfoerderungen-in-den-bundeslaendern-74006914', qt:'ÖAMTC, Stand 9. November 2026'},
    wien:{n:'Wien', kauf:'Keine Kaufförderung für Privatpersonen.', wb:KEINE,
          q:'https://www.oeamtc.at/thema/elektromobilitaet/e-mobilitaetsfoerderungen-in-den-bundeslaendern-74006914', qt:'ÖAMTC, Stand 9. November 2026'},
    noe:{n:'Niederösterreich', kauf:'Keine Kaufförderung für Privatpersonen (nur für Gemeinden).', wb:KEINE,
          q:'https://www.oeamtc.at/thema/elektromobilitaet/e-mobilitaetsfoerderungen-in-den-bundeslaendern-74006914', qt:'ÖAMTC, Stand 9. November 2026'},
    sbg:{n:'Salzburg', kauf:'Keine Kaufförderung für Privatpersonen.', wb:KEINE,
          q:'https://www.oeamtc.at/thema/elektromobilitaet/e-mobilitaetsfoerderungen-in-den-bundeslaendern-74006914', qt:'ÖAMTC, Stand 9. November 2026'},
    ktn:{n:'Kärnten', kauf:'Keine Kaufförderung für Privatpersonen.', wb:KEINE,
          q:'https://www.oeamtc.at/thema/elektromobilitaet/e-mobilitaetsfoerderungen-in-den-bundeslaendern-74006914', qt:'ÖAMTC, Stand 9. November 2026'}
  };
  var sel = document.getElementById('land');
  function zeigen(){
    var d = D[sel.value];
    document.getElementById('t-land').textContent = d.n;
    document.getElementById('r-kauf').textContent = d.kauf;
    document.getElementById('r-wb').textContent = d.wb;
    var a = document.getElementById('r-q'); a.href = d.q; a.textContent = d.qt;
    if (history.replaceState) history.replaceState(null, '', '#' + sel.value);
  }
  var h = (location.hash || '').slice(1);
  if (D[h]) sel.value = h;
  sel.addEventListener('change', zeigen);
  zeigen();
})();
</script>"""

def rechner():
    path = "/foerder-check/"
    graph = [ORG,
             {"@type": "WebApplication", "name": "E-Auto- und Wallbox-Förder-Check Österreich", "url": SITE + path,
              "applicationCategory": "ReferenceApplication", "operatingSystem": "Web", "inLanguage": "de-AT",
              "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
              "description": "Zeigt für jedes österreichische Bundesland, welche Förderungen es 2026 für den Kauf eines E-Autos und für eine Wallbox gibt."},
             breadcrumb_ld(("Förder-Check", path))]
    optionen = "".join(f'<option value="{k}">{n}</option>' for k, n in [
        ("wien", "Wien"), ("noe", "Niederösterreich"), ("bgld", "Burgenland"), ("ooe", "Oberösterreich"), ("stmk", "Steiermark"),
        ("ktn", "Kärnten"), ("sbg", "Salzburg"), ("tirol", "Tirol"), ("vbg", "Vorarlberg")])
    inhalt = f"""<div class="w pad-s">
{crumbs((None, "Förder-Check"))}
<p class="eyebrow">Förder-Check · Stand 9. November 2026</p>
<h1 style="font-size:clamp(32px,4.4vw,48px)">E-Auto- und Wallbox-Förderung nach Bundesland</h1>
<p class="lead">Wählen Sie Ihr Bundesland. Sie sehen, was 2026 für den Kauf eines E-Autos und für eine Wallbox gefördert wird und was in ganz Österreich gilt.</p>
<div class="calc">
<form id="calc" novalidate>
<div class="card">
<div class="field"><label for="land">Ihr Bundesland (Hauptwohnsitz)</label><select id="land">{optionen}</select></div>
<p class="hint">Förderungen ändern sich laufend. Prüfen Sie vor dem Kauf die aktuelle Richtlinie; der Link zur Quelle steht im Ergebnis.</p>
</div>
<div class="card">
<h2 style="font-size:19px;margin:0 0 10px">In ganz Österreich</h2>
<ul class="check" style="margin:0;padding-left:0;font-size:15px">
<li>Keine Kaufprämie des Bundes für Privatpersonen; die Bundesförderung für private Ladestationen ist am 31. März 2026 ausgelaufen.</li>
<li>E-Autos sind von der NoVA befreit, auch beim Import eines Gebrauchtwagens.</li>
<li>Seit 1. April 2025 fällt auch für E-Autos motorbezogene Versicherungssteuer an.</li>
<li>Zahlt der Arbeitgeber die Ladestation daheim, sind die ersten 2.000 € steuerfrei.</li>
<li>Ladestationen über 3,68 kVA müssen beim Netzbetreiber gemeldet werden.</li>
</ul>
</div>
</form>
<aside class="out" aria-live="polite">
<div class="total"><p class="k">Ihr Bundesland</p><p class="v" id="t-land" style="font-size:34px">–</p><p class="s">Förderungen für Privatpersonen 2026</p></div>
<div class="card" style="margin-top:16px">
<h2 style="font-size:19px;margin:0 0 6px">Kauf eines E-Autos</h2>
<p id="r-kauf" style="margin:0 0 18px;font-size:15px;color:var(--body)"></p>
<h2 style="font-size:19px;margin:0 0 6px">Wallbox daheim</h2>
<p id="r-wb" style="margin:0 0 18px;font-size:15px;color:var(--body)"></p>
<p class="hint">Quelle: <a id="r-q" href="#"></a></p>
</div>
</aside>
</div>
<section class="w narrow" style="padding:48px 0 0">
<h2 class="h2" style="font-size:28px">Mehr zum Thema</h2>
<p>Alle Details zur Kaufförderung, zur NoVA und zu den Folgen für den Gebrauchtkauf stehen im Ratgeber <a href="/ratgeber/e-auto-foerderung-oesterreich/">E-Auto-Förderung Österreich 2026</a>. Kosten, Förderbedingungen und Meldepflicht der Wallbox erklärt <a href="/ratgeber/wallbox-kosten-foerderung/">Wallbox in Österreich</a>.</p>
<p class="legal-note">Der Förder-Check fasst öffentliche Angaben der Länder und des ÖAMTC zusammen, Stand 9. November 2026. Er ersetzt nicht die Förderrichtlinie; es besteht kein Rechtsanspruch auf Förderungen. Ihre Auswahl bleibt in Ihrem Browser.</p>
</section>
</div>"""
    return seite("E-Auto & Wallbox Förderung nach Bundesland | netzautos",
                 "Förder-Check 2026: Welche Förderung es in Ihrem Bundesland für den Kauf eines E-Autos und für eine Wallbox gibt. Alle 9 Bundesländer, mit Quellen.",
                 path, graph, inhalt + RECHNER_JS, current="/foerder-check/")

# ---------- Rechtliches ----------

LEGAL_CSS = '<style>.legal h2{font-size:21px;margin:32px 0 8px}.legal p,.legal li{color:var(--body)}</style>\n'

def impressum():
    inhalt = """<div class="w narrow legal" style="padding-block:56px 72px">
<h1 style="font-size:clamp(30px,4vw,42px)">Impressum</h1>
<p>Informationen nach § 5 E-Commerce-Gesetz und Offenlegung nach § 25 Mediengesetz</p>
<h2>Medieninhaber und Betreiber</h2>
<p>FRABANTO AUSTRIA GmbH<br>Theodor-Körner-Gasse 34, 1210 Wien, Österreich</p>
<p>Geschäftsführer: Mag. Anton Scharmitzer<br>Firmenbuch: FN 486022p, Handelsgericht Wien<br>UID-Nummer: ATU73086117<br>E-Mail: office@frabanto.eu</p>
<p>Mitglied der Wirtschaftskammer Wien. Gewerbebehörde: Magistratisches Bezirksamt für den 21. Bezirk. Anwendbare Rechtsvorschriften: Gewerbeordnung, abrufbar unter <a href="https://www.ris.bka.gv.at/">ris.bka.gv.at</a>.</p>
<h2>Grundlegende Richtung</h2>
<p>Allgemeine, unabhängige Information für Käuferinnen und Käufer gebrauchter Elektroautos in Österreich: Förderungen, Laden, Modelle und Kauf.</p>
<h2>Hinweis</h2>
<p>Die Inhalte sind sorgfältig recherchiert und mit Quellen und Prüfdatum versehen, ersetzen aber keine Rechts- oder Steuerberatung. Förderangaben ändern sich; verbindlich ist die jeweils gültige Richtlinie. Für Inhalte verlinkter fremder Websites sind deren Betreiber verantwortlich.</p>
</div>"""
    return seite("Impressum | netzautos", "Impressum und Offenlegung von netzautos.at.", "/impressum/", None, inhalt,
                 robots="noindex, follow", extra=LEGAL_CSS)

def datenschutz():
    inhalt = """<div class="w narrow legal" style="padding-block:56px 72px">
<h1 style="font-size:clamp(30px,4vw,42px)">Datenschutzerklärung</h1>
<p>Stand: November 2026</p>
<h2>Wer ist verantwortlich?</h2>
<p>FRABANTO AUSTRIA GmbH, Theodor-Körner-Gasse 34, 1210 Wien, Österreich, E-Mail office@frabanto.eu.</p>
<h2>Besuch der Website</h2>
<p>Beim Aufruf verarbeitet der Server technisch notwendige Daten (IP-Adresse, Zeitpunkt, aufgerufene Seite, Browser), um die Seite auszuliefern und vor Missbrauch zu schützen (Art. 6 Abs. 1 lit. f DSGVO). Diese technischen Protokolle werden nur kurzfristig gespeichert. Wir setzen keine Cookies, keine Analyse- oder Werbedienste ein und binden keine Schriften oder Skripte fremder Anbieter ein.</p>
<h2>Förder-Check</h2>
<p>Ihre Auswahl im Förder-Check werden ausschließlich in Ihrem Browser verarbeitet. Sie werden nicht an uns übertragen und nicht gespeichert.</p>
<h2>Hosting</h2>
<p>Die Website wird bei Vercel Inc., 440 N Barranca Ave #4133, Covina, CA 91723, USA, gehostet (Art. 6 Abs. 1 lit. f DSGVO, berechtigtes Interesse an einem sicheren und zuverlässigen Betrieb). Da Vercel ein US-Unternehmen ist, kann ein Zugriff aus den USA nicht ausgeschlossen werden. Vercel ist nach dem EU-US Data Privacy Framework zertifiziert; für diese Übermittlung besteht damit ein Angemessenheitsbeschluss der EU-Kommission (Art. 45 DSGVO).</p>
<h2>Ihre Rechte</h2>
<p>Sie haben das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit und Widerspruch. Wenden Sie sich dazu an office@frabanto.eu. Beschwerden können Sie bei der Österreichischen Datenschutzbehörde einbringen (<a href="https://www.dsb.gv.at/">dsb.gv.at</a>).</p>
</div>"""
    return seite("Datenschutz | netzautos", "Datenschutzerklärung von netzautos.at.", "/datenschutz/", None, inhalt,
                 robots="noindex, follow", extra=LEGAL_CSS)

def nicht_gefunden():
    inhalt = """<div class="w narrow legal" style="padding-block:56px 72px">
<h1 style="font-size:clamp(30px,4vw,42px)">Diese Seite gibt es nicht</h1>
<p>Vielleicht hilft Ihnen einer dieser Wege weiter:</p>
<p><a href="/">Zur Startseite</a> · <a href="/ratgeber/">Ratgeber</a> · <a href="/foerder-check/">Förder-Check</a></p>
</div>"""
    return seite("Seite nicht gefunden | netzautos", "Diese Seite gibt es auf netzautos.at nicht.", "/404", None, inhalt,
                 robots="noindex, follow")

# ---------- Sitemap und llms.txt ----------

def sitemap(alle):
    seiten = [("/", STAND), ("/ratgeber/", max(a["modified"] for a in alle)), ("/foerder-check/", STAND)]
    seiten += [(f"/ratgeber/{a['handle']}/", a["modified"]) for a in alle]
    zeilen = "\n".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{d}</lastmod></url>" for p, d in seiten)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{zeilen}\n</urlset>\n'

def llms(alle):
    artikel = "\n".join(f"- [{a['h1']}]({SITE}/ratgeber/{a['handle']}/): {a['desc']}" for a in alle)
    return f"""# netzautos

> Unabhängiger Ratgeber für den Kauf gebrauchter Elektroautos in Österreich. Erklärt Förderungen nach Bundesland, NoVA, Wallbox und Laden daheim, mit Quellenangaben und Prüfdatum.

netzautos.at richtet sich an Menschen in Österreich, die ein gebrauchtes E-Auto kaufen und daheim laden wollen. Alle Inhalte beziehen sich auf österreichische Regeln und Förderungen.

Kernfakten (Stand 9. November 2026):
- Keine Kaufprämie des Bundes für Privatpersonen 2026. Das Programm „E-Mobilität für Private 2024“ endete vorzeitig, das Nachfolgeprogramm (nur E-Zweiräder und Ladeinfrastruktur) lief am 31. März 2026 aus.
- Burgenland ist 2026 das einzige Bundesland mit Kaufförderung für Privatpersonen: 10 % des Anschaffungspreises, höchstens 2.000 €, Preis bis 50.000 €, nur Neuanschaffung (Klasse M1), Antrag binnen 6 Monaten ab Rechnung.
- Wallbox im Einfamilienhaus: nur Burgenland (30 %, höchstens 300 €) und Steiermark (30 %, höchstens 300 €; 11 kW, intelligent, Ökostrom oder PV ab 1,5 kWp, 7 Jahre Betrieb). Vorarlberg fördert nur Mehrparteienhäuser (300 € je Stellplatz, höchstens 10.000 €).
- E-Autos sind von der NoVA befreit (0 g CO₂/km), auch beim Import eines Gebrauchtwagens. Motorbezogene Versicherungssteuer gilt seit 1. April 2025 auch für E-Autos.
- Ladestationen über 3,68 kVA sind beim Netzbetreiber meldepflichtig; bei Netz NÖ zusätzlich Genehmigung ab 10 kW.

## Seiten

- [Startseite]({SITE}/): Überblick, Kernfakten 2026, drei Schritte zum gebrauchten E-Auto, häufige Fragen
- [Förder-Check]({SITE}/foerder-check/): Förderungen für E-Auto-Kauf und Wallbox in allen 9 Bundesländern
- [Ratgeber-Übersicht]({SITE}/ratgeber/): alle Artikel
{artikel}

## Optional

- [Impressum]({SITE}/impressum/)
- [Datenschutz]({SITE}/datenschutz/)
"""

if __name__ == "__main__":
    def schreibe(rel, text):
        ziel = ROOT / rel
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_text(text, encoding="utf-8")
        print("geschrieben:", rel)
    for a in ARTIKEL:
        assert len(a["seo"]) <= 60, (a["handle"], len(a["seo"]))
        assert len(a["desc"]) <= 155, (a["handle"], len(a["desc"]))
        schreibe(f"ratgeber/{a['handle']}/index.html", artikel_seite(a, ARTIKEL))
    schreibe("ratgeber/index.html", uebersicht(ARTIKEL))
    schreibe("index.html", startseite())
    schreibe("foerder-check/index.html", rechner())
    schreibe("impressum/index.html", impressum())
    schreibe("datenschutz/index.html", datenschutz())
    schreibe("404.html", nicht_gefunden())
    schreibe("sitemap.xml", sitemap(ARTIKEL))
    schreibe("llms.txt", llms(ARTIKEL))
