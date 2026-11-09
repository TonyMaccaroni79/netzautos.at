# netzautos.at – Arbeitsanleitung

Ratgeber-Seite für den Kauf gebrauchter Elektroautos in Österreich (Förderung, Laden daheim, Modelle, Kauf). Betreiber: FRABANTO AUSTRIA GmbH, Mag. Anton Scharmitzer. Sprache: Deutsch (Österreich), Sie-Form, sachlich. Die Domain hatte früher eine Gebrauchtwagen-Suchmaschine; Inhalte bleiben beim Thema Auto.

## Aufbau
- Repository-Wurzel = veröffentlichte Seite (statische HTML-Dateien) + `vercel.json`. Vercel baut nichts.
- ALLE Seiten erzeugt `_quelle/build.py` (Startseite, Förder-Check, Ratgeber, Impressum, Datenschutz, 404, sitemap.xml, llms.txt). Nie die erzeugten HTML-Dateien direkt bearbeiten. Bauen: `cd _quelle && python3 build.py`.
- Ratgeber: Text in `_quelle/ratgeber/<handle>.html`, Metadaten in `ARTIKEL` (SEO-Titel ≤ 60 Zeichen, Beschreibung ≤ 155 Zeichen). Schema (Article, FAQ, Breadcrumb) entsteht automatisch.
- Artikel-Aufbau: erster Absatz `<strong>Die kurze Antwort:</strong>`, H2 als Fragen, Tabelle oder Checkliste, `<h2>Häufige Fragen</h2>` mit 3–6 `<h3>` + genau einem `<p>`, am Ende `<h2>Quellen</h2>` mit Prüfdatum.
- Förder-Check: Daten je Bundesland im Objekt `D` in `RECHNER_JS`. Bei jeder Änderung einer Landesförderung dort, in den Artikeln und in `llms()` gleichzeitig ändern.
- Schrift lokal; keine Fremd-Skripte, keine Cookies. Auf `*.vercel.app` liefert `vercel.json` `X-Robots-Tag: noindex`.
- Neue Seite: IndexNow anpingen: `https://api.indexnow.org/indexnow?url=<neue URL>&key=d2163f435a405db0cf2e3ddc8bd1ce64`.

## Hosting-Regel (Vercel Hobby)
- Solange das Projekt im Gratis-Plan läuft: keine Preise, Kaufbuttons, Elektriker-/Lead-Formulare, Werbung oder Affiliate-Links. Kommerzielle Teile (E-Auto-Check-Report, Wallbox-Angebote) erst nach Umzug auf Hetzner oder Vercel Pro.

## Inhaltliche Regeln
- Förderungen ändern sich laufend: jede Angabe an der Landes-Richtlinie oder dem Infoblatt prüfen (burgenland.at, steiermark.at, umweltfoerderung.at), ÖAMTC als Zweitquelle. Prüfdatum angeben. Einmal im Monat alle Landesförderungen neu prüfen, zum Jahreswechsel unbedingt.
- Bekannter Widerspruch: ÖAMTC nennt für Burgenland 30 %; das offizielle Infoblatt 2026 nennt 10 %, höchstens 2.000 €. Es gilt das Infoblatt.
- Keine erfundenen Preise oder Reichweiten; Kosten nur mit Quelle.

## Themenliste Ratgeber (nach Priorität, erledigte streichen)
1. ~~E-Auto-Förderung Österreich 2026~~ – erledigt 09.11.2026
2. ~~Wallbox: Kosten, Förderung, Anmeldung~~ – erledigt 09.11.2026
3. Gebrauchtes E-Auto kaufen: Checkliste vor der Probefahrt
4. Akkuzustand prüfen: Tests und Kosten
5. Renault Zoe gebraucht: Batteriemiete oder Kaufakku
6. Audi e-tron / Q4 e-tron gebraucht
7. Nissan Leaf gebraucht
8. Tesla Model 3 gebraucht
9. VW ID.3 gebraucht
10. Reichweite im Winter
11. E-Auto an der Haushaltssteckdose laden
