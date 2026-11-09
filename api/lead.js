// Formular-Eingang. typ=newsletter: Anmeldung mit Double-Opt-in. typ=anfrage: Rückruf/Anfrage
// (nur aktiv, wenn ANFRAGEN_AKTIV=1 gesetzt ist – kommerzielle Formulare erst nach Wahl des Hostings).
import crypto from 'node:crypto';
import { BASE, SITE, ANLIEGEN, jetzt, token, einwilligung, speichern, feld, formular, ipKurz, weiter, mail, GRUSS } from './_lib.js';

export default async function handler(req, res) {
  if (req.method !== 'POST') { res.statusCode = 405; return res.end('nur POST'); }
  let form;
  try { form = await formular(req); } catch { return weiter(res, '/fehler/'); }
  if (feld(form, 'website')) return weiter(res, '/danke/'); // Spam-Falle: still verwerfen
  try {
    const typ = feld(form, 'typ', 20);
    if (typ === 'newsletter') return await newsletter(form, req, res);
    if (typ === 'anfrage' && process.env.ANFRAGEN_AKTIV === '1') return await anfrage(form, req, res);
  } catch (e) {
    console.error('Fehler:', e.message);
  }
  return weiter(res, '/fehler/');
}

const id = () => crypto.randomBytes(5).toString('hex');
const pfad = (z) => `anfragen/${z.replace(/[:]/g, '-')}-${id()}.json`;

async function newsletter(form, req, res) {
  const email = feld(form, 'email', 200);
  if (!email.includes('@') || feld(form, 'newsletter') !== 'ja') return weiter(res, '/fehler/');
  const erstellt = jetzt(), tok = token();
  const anfrage = { erstellt, typ: 'newsletter', quelle: feld(form, 'quelle'), email, ip_kurz: ipKurz(req),
                    einwilligungen: [{ ...einwilligung('newsletter'), token: tok }] };
  const p = pfad(erstellt);
  await speichern(p, anfrage);
  await speichern(`tokens/${tok}.json`, { anfrage: p });
  const txt = `Guten Tag,\n\nSie möchten neue Ratgeber von ${SITE.domain} per E-Mail bekommen. Bitte bestätigen Sie das mit einem Klick:\n` +
    `${BASE}/api/bestaetigen?t=${tok}\n\nWenn Sie nicht klicken, schicken wir Ihnen keine E-Mails und löschen Ihre Adresse nach 6 Monaten.\n` +
    `Abmelden können Sie sich jederzeit hier: ${BASE}/api/abmelden?t=${tok}\n` + GRUSS();
  await mail(email, `Bitte bestätigen: Ratgeber von ${SITE.name}`, txt);
  return weiter(res, '/newsletter-pruefen/');
}

async function anfrage(form, req, res) {
  const name = feld(form, 'name', 80), tel = feld(form, 'telefon', 40), email = feld(form, 'email', 200);
  if (!name || (tel.replace(/\D/g, '').length < 6 && !email.includes('@')) || feld(form, 'einwilligung_anfrage') !== 'ja') {
    return weiter(res, '/fehler/');
  }
  let anliegen = feld(form, 'anliegen', 30);
  if (!ANLIEGEN.has(anliegen)) anliegen = 'anderes';
  const partner = feld(form, 'einwilligung_partner') === 'ja';
  const erstellt = jetzt();
  const a = {
    erstellt, typ: 'anfrage', quelle: feld(form, 'quelle'), anliegen,
    bundesland: feld(form, 'bundesland', 30), plz: feld(form, 'plz', 4), name, telefon: tel, email,
    zeit: feld(form, 'zeit', 30), nachricht: feld(form, 'nachricht', 800), ip_kurz: ipKurz(req),
    einwilligungen: [einwilligung('anfrage'), ...(partner && EINWILLIGUNG_PARTNER ? [einwilligung('partner')] : [])],
  };
  const p = pfad(erstellt);
  await speichern(p, a);
  await mail(process.env.NOTIFY_TO, `Neue Anfrage (${SITE.name}): ${anliegen} · ${a.bundesland}`,
    `Name: ${name}\nTelefon: ${tel}\nE-Mail: ${email}\nAnliegen: ${anliegen}\nBundesland/PLZ: ${a.bundesland} ${a.plz}\n` +
    `Zeit: ${a.zeit}\nWeitergabe an Partner erlaubt: ${partner ? 'ja' : 'nein'}\nQuelle: ${a.quelle}\n\nNachricht:\n${a.nachricht || '-'}\n`);
  return weiter(res, '/danke/');
}

const EINWILLIGUNG_PARTNER = Boolean(SITE.einwilligung.partner);
