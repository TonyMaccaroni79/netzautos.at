// Seitenspezifische Einstellungen fuer die Formulare von netzautos.at.
// Einwilligungstexte exakt wie auf der Seite; Version erhoehen, wenn ein Text geaendert wird.
export const SITE = {
  name: 'netzautos', domain: 'netzautos.at', base: 'https://netzautos.at',
  anliegen: ['wallbox', 'kauf', 'foerderung', 'akku', 'anderes'],
  einwilligung: {
    newsletter: ['v1', 'Ja, ich möchte neue Ratgeber und Förder-Änderungen rund ums E-Auto per E-Mail (höchstens einmal im Monat, jederzeit abbestellbar). Ich bekomme dazu eine Bestätigungs-E-Mail.'],
    anfrage: ['v1', 'Ich möchte, dass netzautos (FRABANTO AUSTRIA GmbH) mich zu meiner Anfrage kontaktiert und meine Angaben dafür speichert. Ich kann das jederzeit widerrufen.'],
    partner: ['v1', 'Freiwillig: Wenn es passt, darf netzautos meine Anfrage an einen geprüften Fachbetrieb (z. B. Elektriker) weitergeben. Welcher Betrieb das ist, erfahre ich vorher und kann dann noch ablehnen.'],
  },
};
