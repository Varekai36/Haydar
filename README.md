# Die Bratküche Erlangen – Website

Website für **Die Bratküche**: Smash Burger & Loaded Fries, Lachnerstraße 2, 91058 Erlangen-Tennenlohe.
Öffnungszeiten: Mo–Do 11–15 & 17–20 Uhr, Fr 11–15 Uhr. Telefon: 0177 6564204. E-Mail: diebratkueche@proton.me.

Die Seite besteht nur aus HTML, CSS und etwas JavaScript. Es gibt keinen Build-Schritt und keine Abhängigkeiten.
Sie läuft direkt auf GitHub Pages oder bei jedem anderen Webhoster.

## Inhalt

| Datei | Zweck |
|---|---|
| `index.html` | Startseite: Burger, Loaded Fries, Fotos, Über uns, Öffnungszeiten & Anfahrt |
| `impressum.html` | Impressum (Vorlage, Adresse schon eingetragen) |
| `datenschutz.html` | Datenschutzerklärung (Vorlage) |
| `assets/css/style.css` | Gestaltung: Farben und Schriften stehen oben in `:root` |
| `assets/js/main.js` | Mobilmenü und Live-Anzeige „Jetzt geöffnet / Mittagspause / Geschlossen“ |
| `assets/img/` | Fotos, Logo und Icons (verkleinert, ohne Standortdaten) |
| `assets/fonts/` | Lokal gespeicherte Schriften (Bebas Neue, Fraunces, DM Sans, Caveat, Lizenz SIL OFL). Es wird nichts von Google geladen. |

## Noch offen

- [ ] **USt-IdNr. (falls vorhanden):** In `impressum.html` ist ein auskommentierter Block vorbereitet. Nummer eintragen und die Kommentar-Zeichen entfernen.
- [ ] **Rechtstexte prüfen lassen:** Impressum und Datenschutzerklärung sind ausgefüllt, aber keine Rechtsberatung. Die Datenschutzerklärung geht von Hosting über GitHub Pages aus. Bei einem anderen Hoster oder neuen Funktionen muss sie angepasst werden.
- [ ] **Eigene Domain:** Sobald die Domain feststeht, bei `og:image` die volle Adresse eintragen, z. B. `https://www.die-bratkueche.de/assets/img/og-image.jpg`. Dann zeigen WhatsApp, Instagram und andere Dienste beim Teilen das Logo als Vorschaubild.

## Speisekarte pflegen

Die Gerichte stehen direkt in `index.html`, jeweils als `<li class="item">`.

**Ein Gericht „Bald verfügbar“ freischalten**, z. B. den Grünschnabel:

1. Bei `<li class="item is-soon">` das `is-soon` entfernen, sodass dort `<li class="item">` steht.
2. `<span class="soon">Bald verfügbar</span>` durch die Preise ersetzen:

```html
<div class="prices">
  <span class="price-box"><small>Double</small>10,90&nbsp;€</span>
  <span class="price-box"><small>Single</small>7,90&nbsp;€</span>
</div>
```

Bei Pommes mit nur einem Preis:

```html
<div class="prices"><span class="price-box price-single">8,90&nbsp;€</span></div>
```

**Markierungen:** `<span class="tag tag-hot">Scharf</span>` oder `<span class="tag tag-veg">Veggie</span>` hinter den Namen setzen.
Handschriftliche Notiz: `<p class="note">Nur für Mutige!</p>`.

## Öffnungszeiten ändern

Die Zeiten stehen in der Tabelle unter `id="zeiten"`:

```html
<tr data-day="1" data-hours="11:00-15:00,17:00-20:00"><th scope="row">Montag</th><td><span>11:00–15:00</span> <span>17:00–20:00</span></td></tr>
```

- `data-day`: 0 = Sonntag, 1 = Montag, …, 6 = Samstag
- `data-hours`: Zeitfenster im Format `HH:MM-HH:MM`, mehrere durch Komma getrennt
- Ruhetag: `data-hours` weglassen und in die Zelle `Geschlossen` schreiben

Daraus berechnet die Seite automatisch, in deutscher Zeit:

- „Jetzt geöffnet · bis 15:00 Uhr“
- „Mittagspause · ab 17:00 Uhr wieder offen“
- „Geschlossen · öffnet morgen um 11:00 Uhr“

Die Zeiten im Kopf der Seite („Mo–Do 11–15 & 17–20 Uhr · Fr 11–15 Uhr“) und in den strukturierten Daten im `<head>` bitte passend mitändern.

## Fotos austauschen

Neue Fotos in `assets/img/` ablegen. Am besten vorher verkleinern (etwa 1000–1800 px breit, JPG oder WebP) und die Standortdaten aus dem Foto entfernen.
Ein Foto von den Loaded Fries würde gut in den Bereich „Loaded Fries“ passen.

## Lokal ansehen

```bash
python3 -m http.server 8000
# dann http://localhost:8000 öffnen
```

## Mit GitHub Pages veröffentlichen

1. Den Branch mit der Website in `main` mergen.
2. Im Repository auf **Settings → Pages** gehen.
3. Unter **Build and deployment** als Quelle **Deploy from a branch** wählen, dann Branch `main` und Ordner `/ (root)`.
4. Nach ungefähr einer Minute ist die Seite unter `https://<benutzername>.github.io/<repository>/` erreichbar.
5. Optional dort die eigene Domain eintragen.
