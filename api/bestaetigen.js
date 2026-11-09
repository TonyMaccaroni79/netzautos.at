import { jetzt, lesen, speichern, weiter } from './_lib.js';

export default async function handler(req, res) {
  const t = (new URL(req.url, 'http://x').searchParams.get('t') || '').replace(/[^A-Za-z0-9_-]/g, '');
  if (!t || !(await lesen(`tokens/${t}.json`))) return weiter(res, '/fehler/');
  if (!(await lesen(`bestaetigt/${t}.json`))) {
    try { await speichern(`bestaetigt/${t}.json`, { bestaetigt: jetzt() }); } catch { /* schon bestaetigt */ }
  }
  return weiter(res, '/newsletter-bestaetigt/');
}
