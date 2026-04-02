# myRadio Stations Editor (HU/EN)

A **myRadio Stations Editor** egy kétnyelvű (magyar/angol) Windows alkalmazás, amely jelentősen megkönnyíti az ESP32-alapú **myRadio** (és részben a **yoRadio**) webrádiók **stations.txt** állomáslistájának kezelését.

Az alkalmazás két módon töltheti be a listát:
- közvetlenül letölti az aktuális lejátszási listát a rádió **IP-címe** alapján,
- vagy betölt egy meglévő állomáslistát a számítógépedről.

---

## Képernyőkép

![myRadio Stations Editor](https://github.com/gidano/myRadio-Editor/blob/main/myRadio_Stations_Editor-HU_v1.1.jpg)

---

## Fő funkciók

- 📡 **Lista letöltése a rádióról** – IP-cím megadásával (myRadio és yoRadio esetén is, utóbbinál a `playlist.csv` fájlt)
- 💾 **Lista betöltése és mentése** a számítógépről / számítógépre  
  (olvassa a yoRadio `.csv` formátumát is, belsőleg `stations.txt` formátumban kezeli és menti)
- ✏️ **Állomások részletes szerkesztése** (név, stream URL, stb.)
- ✏️ **Képesség az állomásnév kis/nagy betűsre alakaítása**
- 🔤 **ABC szerinti rendezés** egy kattintással
- 🖱️ **Drag & drop átrendezés** – az állomásokat szabadon húzogatva tetszőleges sorrendbe rakhatod
- ➕ **Másik lista hozzáfűzése** (több lista egyesítése)
- 📤 **Lista visszatöltése a rádióra**  
  → újraindítás után a rádió már az új, módosított listát használja

---

## Ellenőrző és karbantartó funkciók

- ✔️ **Stream URL-ek működésének ellenőrzése** (működik-e az adott állomás)
- 🔍 **Duplikált állomások automatikus keresése**
- 🧹 **Duplikátumok törlése**  
  – egyesével  
  – vagy **egy gombnyomással az összes** duplikátum

---

## Lista szerkesztés

- 🆕 **Új állomások** hozzáadása
- 📄 Meglévő állomások **duplikálása** (biztonságos szerkesztéshez)
- ✏️ A teljes lista szabad szerkesztése táblázatos felületen

---

## Használati cél

A program célja, hogy a **stations.txt** fájl szerkesztése kényelmes, grafikus felületen történjen, anélkül, hogy kézzel kellene szövegszerkesztőben módosítanod a fájlt.

Az exe fájl mérete nagyobb (kb. 30–40 MB), mert **tartalmazza a Python és Qt futtatókörnyezetet** is. Így nem kell külön telepítened semmit a számítógépedre – egyszerűen csak futtatod az exe-t.

---

## English Version

**myRadio Stations Editor** is a bilingual (Hungarian/English) Windows application that makes managing the station list (**stations.txt**) of **myRadio** (and partially **yoRadio**) internet radios significantly easier.

The application can load the playlist in two ways:
- by downloading the current station list directly from the radio using its **IP address**,
- or by loading an existing list from your computer.

---

### Screenshot

![myRadio Stations Editor](https://github.com/gidano/myRadio-Editor/blob/main/myRadio_Stations_Editor-EN_v1.1.jpg)

---

### Main Features

- 📡 **Download list from the radio** via IP address (supports both myRadio and yoRadio – for yoRadio it uses the `playlist.csv` file)
- 💾 **Load and save list** from/to PC  
  (It also reads the yoRadio `.csv` format, but internally handles and saves it in the `stations.txt` format)
- ✏️ **Detailed station editing** (name, stream URL, etc.)
- ✏️ **Ability to convert station names to uppercase or lowercase**
- 🔤 **Sort alphabetically** with one click
- 🖱️ **Drag & drop reordering** – freely rearrange any station in the desired order
- ➕ **Append another list** (merge multiple station lists)
- 📤 **Upload list back to the radio**  
  → after restarting the radio, it will use the new, modified list

---

### Checking and Maintenance Tools

- ✔️ **Verify stream URLs** – check whether each station is working
- 🔍 **Find duplicate stations** automatically
- 🧹 **Remove duplicates**  
  – individually  
  – or **all duplicates at once** with a single button

---

### Station List Editing

- 🆕 Add new stations
- 📄 **Duplicate** existing stations (for safe editing)
- ✏️ Full free editing of the entire list in a table view

---

### Purpose

The goal of the program is to allow comfortable, graphical editing of the **stations.txt** file without the need for manual text editing, which often leads to errors.

The executable is larger (~30–40 MB) because it **includes the Python and Qt runtime**. No additional installation is required on your PC – just run the .exe file.

---

## Direct Download

**[Download myRadio Stations Editor v1.0](https://github.com/gidano/myRadio-Editor/releases/tag/1.0)**

---

Ha szeretnéd, hogy még részletesebb legyen (pl. rendszerkövetelmények, telepítési útmutató, changelog, vagy támogatott rádiók listája), vagy ha finomhangolást szeretnél a szövegen, nyugodtan mondd meg!
