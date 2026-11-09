import crypto from 'node:crypto';
import { alle, lesen, SITE } from './_lib.js';

const SPALTEN = ['erstellt', 'typ', 'anliegen', 'bundesland', 'plz', 'name', 'telefon', 'email', 'zeit', 'nachricht', 'quelle', 'einwilligungen', 'newsletter_bestaetigt', 'newsletter_abgemeldet', 'datei'];

function gleich(a, b) {
  const x = Buffer.from(a || ''), y = Buffer.from(b || '');
  return x.length === y.length && x.length > 0 && crypto.timingSafeEqual(x, y);
}

const zelle = (v) => {
  const s = v == null ? '' : typeof v === 'object' ? JSON.stringify(v) : String(v);
  return /[;"\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};

export default async function handler(req, res) {
  const key = new URL(req.url, 'http://x').searchParams.get('key');
  if (!gleich(key, process.env.EXPORT_KEY)) { res.statusCode = 403; return res.end('kein Zugriff'); }
  const [anfragen, best, abg] = await Promise.all([alle('anfragen/'), alle('bestaetigt/'), alle('abgemeldet/')]);
  const tokName = (b) => b.pathname.split('/')[1].replace('.json', '');
  const bestMap = new Map(await Promise.all(best.map(async (b) => [tokName(b), (await lesen(b.pathname))?.bestaetigt])));
  const abgMap = new Map(await Promise.all(abg.map(async (b) => [tokName(b), (await lesen(b.pathname))?.widerrufen])));
  const zeilen = (await Promise.all(anfragen.map(async (b) => ({ ...(await lesen(b.pathname)), datei: b.pathname }))))
    .filter((a) => a.erstellt)
    .sort((a, b) => (a.erstellt < b.erstellt ? 1 : -1))
    .map((a) => {
      const nl = (a.einwilligungen || []).find((e) => e.art === 'newsletter');
      return {
        ...a,
        einwilligungen: (a.einwilligungen || []).map((e) => `${e.art} ${e.version} ${e.erteilt}`).join(' | '),
        newsletter_bestaetigt: nl ? bestMap.get(nl.token) || '' : '',
        newsletter_abgemeldet: nl ? abgMap.get(nl.token) || '' : '',
      };
    });
  const csv = [SPALTEN.join(';'), ...zeilen.map((z) => SPALTEN.map((s) => zelle(z[s])).join(';'))].join('\r\n');
  res.setHeader('Content-Type', 'text/csv; charset=utf-8');
  res.setHeader('Content-Disposition', `inline; filename="${SITE.name}-anfragen.csv"`);
  res.setHeader('Cache-Control', 'no-store');
  res.end('﻿' + csv);
}
