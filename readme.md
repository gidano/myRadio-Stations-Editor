# myRadio Stations Editor

## 🇭🇺 Leírás

A **myRadio Stations Editor** egy egyszerű, mégis hatékony Windows alkalmazás, amely ESP32 alapú internet rádiók állomáslistájának kezelésére készült.

Elsődleges célja a **myRadio** .txt, de támogatja a **ëRadio** .csv formátumát is.

## Képernyőkép

![myRadio Stations Editor](https://github.com/gidano/myRadio-Editor/blob/main/myRadio_Stations_Editor-HU_v1.2.jpg)

## ✨ Fő funkciók

* Állomáslista szerkesztése (név + URL + logó)
* ëRadio kompatibilis CSV kezelés (hangerővel)
* myRadio kompatibilis TXT kezelés (logó támogatással)
* Két formátum közti konverzió
* Közvetlen kapcsolat rádióval állomáslista le/feltöltésére (IP alapján)
* Állomások ellenőrzése:

  * hibás URL
  * nem elérhető stream
  * duplikációk
* Keresés és szűrés
* Undo / Redo
* Drag & drop rendezés
* Automatikus backup mentés

## 📁 Támogatott formátumok

### myRadio

Station Name<TAB>URL<TAB>Logo

A harmadik mező az állomás logójának neve (kiterjesztés nélkül).

Példa:
DANUBIUS RÁDIÓ	https://...	danubius

Szabályok:
* a logónév kisbetűs
* nem tartalmaz kiterjesztést (.png automatikus)
* ha nincs logó: nologo
* a rádió a /logos mappából tölti be (pl. /logos/danubius.png)

### ëRadio

Station Name<TAB>URL<TAB>Volume

A hangerő (volume) érték megmarad szerkesztés és mentés során.

## 🌐 Rádió támogatás

### myRadio

* Beolvasás: /api/stations
* Feltöltés: /upload → /stations.txt

### ëRadio

* Beolvasás: /data/playlist.csv
* Feltöltés: /upload (plfile)

## 🔄 Konverzió

* CSV → TXT (ëRadio → myRadio)
* TXT → CSV (myRadio → ëRadio)

Automatikusan történik mentéskor a fájlkiterjesztés alapján.

## 🧠 Használat

1. Add meg a rádió IP címét
2. Válaszd ki a típust (Auto / myRadio / ëRadio)
3. Olvasd be a listát vagy nyiss meg fájlt
4. Szerkeszd az állomásokat (név, URL és logó)
5. Mentsd vagy töltsd vissza a rádióra

## ⚠️ Megjegyzések

* ëRadio esetén a hangerő oszlop fontos
* myRadio esetén a logó mező a /logos mappában lévő PNG fájlra hivatkozik
* Ha a logó nem található, a rádió automatikusan a nologo.png fájlt használja
* Feltöltés után a rádió újraindítása szükséges lehet
* Backup automatikusan készül mentés előtt

---

## 🇬🇧 Description

**myRadio Stations Editor** is a lightweight Windows application designed to manage station lists for ESP32-based internet radios.

It primarily targets **myRadio** .txt, but also supports **ëRadio** .csv format.

### Screenshot

![myRadio Stations Editor](https://github.com/gidano/myRadio-Editor/blob/main/myRadio_Stations_Editor-EN_v1.2.jpg)

## ✨ Features

* Edit station list (name + URL + logo)
* ëRadio CSV support (with volume)
* myRadio TXT support (with logo handling)
* Format conversion between TXT and CSV
* Direct connection to a radio for down/uploading station lists (based on IP address)
* Station validation:

  * invalid URLs
  * unreachable streams
  * duplicates
* Search and filtering
* Undo / Redo
* Drag & drop reordering
* Automatic backup before saving

## 📁 Supported formats

### myRadio

Station Name<TAB>URL<TAB>Logo

The third field defines the station logo name (without file extension).

Example:
DANUBIUS RADIO	https://...	danubius

Rules:
* logo names must be lowercase
* no file extension (.png is added automatically)
* use "nologo" if no logo is available
* logos are loaded from /logos (e.g. /logos/danubius.png)

### ëRadio

Station Name<TAB>URL<TAB>Volume

Volume values are preserved during editing and saving.

## 🌐 Radio support

### myRadio

* Read: /api/stations
* Write: /upload → /stations.txt

### ëRadio

* Read: /data/playlist.csv
* Write: /upload (plfile)

## 🔄 Conversion

* CSV → TXT (ëRadio → myRadio)
* TXT → CSV (myRadio → ëRadio)

Handled automatically based on file extension.

## 🧠 Usage

1. Enter radio IP address
2. Select type (Auto / myRadio / ëRadio)
3. Read list or open file
4. Edit stations (name, URL and logo)
5. Save or upload back to radio

## ⚠️ Notes

* Volume column is important for ëRadio
* For myRadio, the logo field references PNG files in the /logos directory
* If a logo is missing, the radio automatically falls back to nologo.png
* Radio restart may be required after upload
* Backup is created automatically before saving