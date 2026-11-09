// Taeglich per Vercel Cron: Anfragen ohne bestaetigten Newsletter nach 180 Tagen loeschen (Datenschutzerklaerung).
import { alle, lesen, del, LOESCHEN_NACH_TAGEN } from './_lib.js';

export default async function handler(req, res) {
  if (!process.env.CRON_SECRET || req.headers.authorization !== `Bearer ${process.env.CRON_SECRET}`) {
    res.statusCode = 401; return res.end('kein Zugriff');
  }
  const grenze = Date.now() - LOESCHEN_NACH_TAGEN * 864e5;
  const alt = (await alle('anfragen/')).filter((b) => new Date(b.uploadedAt).getTime() < grenze);
  let geloescht = 0;
  for (const b of alt) {
    const a = await lesen(b.pathname);
    const nl = (a?.einwilligungen || []).find((e) => e.art === 'newsletter');
    if (nl && (await lesen(`bestaetigt/${nl.token}.json`)) && !(await lesen(`abgemeldet/${nl.token}.json`))) continue;
    const weg = [b.url];
    if (nl) {
      for (const p of [`tokens/${nl.token}.json`, `bestaetigt/${nl.token}.json`, `abgemeldet/${nl.token}.json`]) {
        const t = (await alle(p))[0];
        if (t) weg.push(t.url);
      }
    }
    await del(weg);
    geloescht++;
  }
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify({ geprueft: alt.length, geloescht }));
}
