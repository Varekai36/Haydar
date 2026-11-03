# Bratküche – Website

Eine Website für die **Bratküche** auf einer einzigen Seite. Sie besteht nur aus HTML, CSS und etwas JavaScript.
Es gibt keinen Build-Schritt und keine Abhängigkeiten. Die Seite läuft direkt auf GitHub Pages oder bei jedem anderen Webhoster.

## Inhalt

| Datei | Zweck |
|---|---|
| `index.html` | Startseite mit Speisekarte, Über uns, Öffnungszeiten und Kontakt |
| `impressum.html` | Impressum (Vorlage) |
| `datenschutz.html` | Datenschutzerklärung (Vorlage) |
| `assets/css/style.css` | Gestaltung: Farben und Schriften stehen oben in `:root` |
| `assets/js/main.js` | Mobilmenü, Filter der Speisekarte, Anzeige „Jetzt geöffnet“ |
| `assets/fonts/` | Lokal gespeicherte Schriften (Fraunces, DM Sans, Lizenz SIL OFL). Es wird nichts von Google geladen. |
| `assets/img/favicon.svg` | Symbol im Browser-Tab |

## Vor dem Veröffentlichen anpassen

Alle Stellen sind in `index.html` mit `<!-- ANPASSEN -->` markiert.

- [ ] **Adresse:** `Musterstraße 12, 12345 Musterstadt`. Kommt im Kontaktbereich, im Link „Route planen“, in den strukturierten Daten im `<head>` und in den Rechtstexten vor.
- [ ] **Telefon:** `0123 456789` bzw. `tel:+49123456789`. Kommt in der Kopfzeile, im Hero, im Kontaktbereich und in den Rechtstexten vor.
- [ ] **E-Mail:** `kontakt@ihre-domain.de`
- [ ] **Speisekarte:** Gerichte, Beschreibungen und Preise. Die aktuellen Preise sind nur **Beispielwerte**.
- [ ] **Mittagstisch:** Tage, Uhrzeit und Preis, oder den Block `<aside class="lunch">` löschen.
- [ ] **Öffnungszeiten:** in der Tabelle unter `id="zeiten"` (siehe unten).
- [ ] **Über uns:** eure eigene Geschichte.
- [ ] **Impressum & Datenschutz:** alle Angaben in `[eckigen Klammern]` ersetzen und danach den gelben Hinweis „Vorlage“ löschen. Die Texte sind eine Vorlage und keine Rechtsberatung.

### Öffnungszeiten ändern

Jede Zeile der Tabelle hat drei Angaben:

```html
<tr data-day="2" data-open="11:00" data-close="21:00"><th scope="row">Dienstag</th><td>11:00 – 21:00</td></tr>
```

- `data-day`: 0 = Sonntag, 1 = Montag, …, 6 = Samstag
- `data-open` und `data-close` im Format `HH:MM`
- Ruhetag: `data-open` und `data-close` weglassen

Aus diesen Angaben berechnet die Seite automatisch „Jetzt geöffnet · bis 21:00 Uhr“ bzw. „Gerade geschlossen · öffnet morgen um …“.
Gerechnet wird immer in deutscher Zeit. Den sichtbaren Text in `<td>` bitte passend mitändern.

### Eigene Fotos einbinden

Fotos in `assets/img/` ablegen und an der gewünschten Stelle einbinden, zum Beispiel:

```html
<img src="assets/img/schnitzel.jpg" alt="Schnitzel mit Bratkartoffeln" width="800" height="600" loading="lazy">
```

Am besten verkleinert als JPG oder WebP, ungefähr 1600 px breit und unter 300 KB.

## Lokal ansehen

`index.html` einfach im Browser öffnen. Damit die Schriften auch lokal korrekt laden, besser einen kleinen Server starten:

```bash
python3 -m http.server 8000
# dann http://localhost:8000 öffnen
```

## Mit GitHub Pages veröffentlichen

1. Den Branch mit der Website in `main` mergen.
2. Im Repository auf **Settings → Pages** gehen.
3. Unter **Build and deployment** als Quelle **Deploy from a branch** wählen, dann Branch `main` und Ordner `/ (root)`.
4. Nach ungefähr einer Minute ist die Seite unter `https://<benutzername>.github.io/<repository>/` erreichbar.
5. Optional kann man dort auch eine eigene Domain eintragen, z. B. `www.bratkueche-musterstadt.de`.
