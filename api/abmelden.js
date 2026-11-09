import { jetzt, lesen, speichern } from './_lib.js';

export default async function handler(req, res) {
  const t = (new URL(req.url, 'http://x').searchParams.get('t') || '').replace(/[^A-Za-z0-9_-]/g, '');
  if (t && (await lesen(`tokens/${t}.json`)) && !(await lesen(`abgemeldet/${t}.json`))) {
    try { await speichern(`abgemeldet/${t}.json`, { widerrufen: jetzt() }); } catch { /* schon abgemeldet */ }
  }
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  res.end("<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width'><p style='font:20px system-ui;margin:40px'>Sie sind abgemeldet. Wir schicken Ihnen keine Newsletter mehr.</p>");
}
