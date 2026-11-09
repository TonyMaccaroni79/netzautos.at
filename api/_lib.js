// Gemeinsame Logik fuer die Formulare (Vercel Functions, Node). Gleicher Aufbau wie daheimklar.at.
// Speicher: privater Vercel-Blob-Store. Jede Anfrage ist eine eigene JSON-Datei.
//   anfragen/<zeit>-<id>.json        Anfrage oder Newsletter-Anmeldung inkl. Einwilligungen
//   tokens/<token>.json              Verweis Newsletter-Token -> Anfrage
//   bestaetigt/<token>.json          Zeitpunkt der Double-Opt-in-Bestaetigung
//   abgemeldet/<token>.json          Zeitpunkt des Widerrufs
// Seitenspezifisches (Name, Einwilligungstexte, Anliegen) steht in _site.js.
import { put, get, list, del } from '@vercel/blob';
import crypto from 'node:crypto';
import { SITE } from './_site.js';

export { SITE };
export const BASE = process.env.SITE_BASE_URL || SITE.base;
export const LOESCHEN_NACH_TAGEN = 180;
export const ANLIEGEN = new Set(SITE.anliegen);
export const EINWILLIGUNG = SITE.einwilligung;

export const jetzt = () => new Date().toISOString().replace(/\.\d+Z$/, 'Z');
export const token = () => crypto.randomBytes(24).toString('base64url');

export function einwilligung(art) {
  const [version, text] = EINWILLIGUNG[art];
  return { art, version, text_hash: crypto.createHash('sha256').update(text).digest('hex'), erteilt: jetzt() };
}

export async function speichern(pfad, daten) {
  return put(pfad, JSON.stringify(daten), {
    access: 'private', contentType: 'application/json', addRandomSuffix: false, allowOverwrite: false,
  });
}

export async function lesen(pfad) {
  try {
    const r = await get(pfad, { access: 'private', useCache: false });
    if (!r || r.statusCode !== 200) return null;
    return JSON.parse(await new Response(r.stream).text());
  } catch { return null; }
}

export async function alle(prefix) {
  const out = [];
  let cursor;
  do {
    const r = await list({ prefix, cursor, limit: 1000 });
    out.push(...r.blobs);
    cursor = r.hasMore ? r.cursor : undefined;
  } while (cursor);
  return out;
}

export { del };

export function feld(body, k, n = 200) {
  const v = body?.[k];
  return (Array.isArray(v) ? v[0] : v || '').toString().trim().slice(0, n);
}

export async function formular(req) {
  if (req.body && typeof req.body === 'object' && !Buffer.isBuffer(req.body)) return req.body;
  let raw = typeof req.body === 'string' ? req.body : '';
  if (!raw) {
    const teile = [];
    for await (const c of req) teile.push(c);
    raw = Buffer.concat(teile).toString('utf8');
  }
  return Object.fromEntries(new URLSearchParams(raw));
}

export function ipKurz(req) {
  const ip = (req.headers['x-real-ip'] || (req.headers['x-forwarded-for'] || '').split(',')[0] || '').trim();
  if (ip.includes(':')) return ip.split(':').slice(0, 3).join(':') + '::';
  const t = ip.split('.');
  return t.length === 4 ? [...t.slice(0, 3), '0'].join('.') : '';
}

export function weiter(res, ziel) {
  res.statusCode = 303;
  res.setHeader('Location', ziel);
  res.setHeader('Cache-Control', 'no-store');
  res.end();
}

export async function mail(an, betreff, text) {
  const { SMTP_HOST: host, SMTP_PORT: port, SMTP_USER: user, SMTP_PASS: pass, SMTP_FROM: from } = process.env;
  if (!host || !from || !an) return false;
  try {
    const nodemailer = (await import('nodemailer')).default;
    const p = Number(port || 465);
    const t = nodemailer.createTransport({ host, port: p, secure: p === 465, auth: user ? { user, pass } : undefined });
    await t.sendMail({ from, to: an, subject: betreff, text });
    return true;
  } catch (e) {
    console.error('Mailfehler:', e.message); // Anfrage ist trotzdem gespeichert
    return false;
  }
}

export const GRUSS = () => `\nHerzliche Grüße\nAnton Scharmitzer, ${SITE.domain}\n\nFRABANTO AUSTRIA GmbH, Theodor-Körner-Gasse 34, 1210 Wien`;
