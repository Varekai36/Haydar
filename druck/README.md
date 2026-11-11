# Druckdateien

## Fensterplakat „Currywurst mit Pommes“

| Datei | Inhalt |
|---|---|
| `fensterplakat_currywurst.py` | Erzeugt das Plakat als druckfertige PDF |
| `Bratkueche_Fensterplakat_Currywurst_A2_VORSCHAU_ohne_Foto.pdf` | Vorschau mit Platzhalter, **noch nicht drucken** |

**Druckdaten:** Endformat A2 (420 × 594 mm), Datenformat 424 × 598 mm, also 2 mm Beschnitt rundum wie beim Flyeralarm-Flyer.
Farben in CMYK, Schriften eingebettet (Bebas Neue, Fraunces, DM Sans, Caveat aus `assets/fonts`).
Der QR-Code führt auf denselben Vorbestell-Link wie der Flyer (`https://su.onl/mfsri42`).

### Foto einsetzen und Druckdatei erzeugen

```bash
pip install reportlab pillow fonttools brotli
python3 druck/fensterplakat_currywurst.py --foto pfad/zum/foto.jpg
```

Das ergibt `druck/Bratkueche_Fensterplakat_Currywurst_A2_Druckdatei.pdf`.

- `--fokus 0.5,0.6` verschiebt den Bildausschnitt (x,y zwischen 0 und 1; 0.5,0.5 = Mitte).
- `--format A1` (oder A3, A0) für eine andere Größe. Alles wird mitskaliert.
- `--beschnitt 3`, falls die Druckerei 3 mm statt 2 mm Beschnitt verlangt.

Das Skript meldet, wie scharf das Foto im Druck wird (ppi). Für A2 sollte das Foto mindestens etwa 2500 px breit sein.
Am besten das Originalfoto vom Handy nehmen. Fotos aus WhatsApp sind meist stark verkleinert.

Preis, Texte, Öffnungszeiten und Adresse stehen oben im Skript unter „Inhalte“.
