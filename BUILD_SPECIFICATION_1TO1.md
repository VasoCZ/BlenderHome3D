# Kompletní 1:1 Stavební a Modelovací Specifikace Projektu BlenderHome3D

Tento dokument představuje **deterministickou, absolutně přesnou technickou specifikaci** rodinného domu pro 3D software **Blender 5.2+**. 
Podle těchto parametrů a vzorců lze kdykoliv postavit **1:1 identický model** bez jakýchkoliv odchylek či nejasností, včetně všech stavebních úprav, interiérového vybavení, osvětlení a exteriérových doplňků.

---

## 1. Architektonické Základy & Globální Souřadnicový Systém

### 1.1 Orientace a počátek souřadnic
- **Počátek $(0.000, 0.000, 0.000)$**: Jihozápadní vnější roh obvodových stěn domu (bez započtení přesahu základové desky či římsy).
- **Osa $+X$**: Směr **VÝCHOD** (šířka domu $10.000\text{ m}$).
- **Osa $+Y$**: Směr **SEVER** (délka domu $12.000\text{ m}$).
- **Osa $+Z$**: Směr **NAHORU** (výška modelu: reálná výška stěn $Z = 2.500\text{ m}$, základová spára $Z = -0.200\text{ m}$).

### 1.2 Hlavní konstrukční rozměry
| Prvek | Rozměry / Tloušťka | Výškový rozsah $Z$ | Popis |
| :--- | :--- | :--- | :--- |
| **Půdorys domu** | $10.000 \times 12.000\text{ m}$ | $0.000 \to 2.500\text{ m}$ | Zastavěná plocha $120.0\text{ m}^2$ |
| **Obvodové stěny** | Tloušťka $0.365\text{ m}$ ($36.5\text{ cm}$) | $0.000 \to 2.500\text{ m}$ | Zdivo Porotherm/Ytong |
| **Vnitřní příčky** | Tloušťka $0.125\text{ m}$ ($12.5\text{ cm}$) | $0.000 \to 2.500\text{ m}$ | Dělící nenosné zdivo |
| **Nášlapná vrstva podlah** | Tloušťka $0.015\text{ m}$ ($15\text{ mm}$) | $0.000 \to 0.015\text{ m}$ | Keramická dlažba / plovoucí laminát |
| **Základová deska & zpevněné plochy** | Tloušťka $0.200\text{ m}$ ($20\text{ cm}$) | $-0.200 \to 0.000\text{ m}$ | Monolitický beton + dlažba |
| **Střešní atika / římsa (Soffit)** | Šířka profilu $0.500\text{ m}$ | $2.420 \to 2.500\text{ m}$ | Vnější obvod $11.0 \times 13.0\text{ m}$ |

---

## 2. Podrobný Rozpis Místností (Room Schedule 1.01 až 1.11)

Všechny místnosti odpovídají oficiálnímu stavebnímu výkresu `Půdorys-aktuální 27.10.2020.png`:

```
+-------------------------------------------------------------------------+ Y = 12.000 m
| 1.10 KOUPELNA        | 1.11 CHODBA  | 1.03 KUCHYNĚ   | 1.04 OBÝVACÍ     |
| (Dlažba / Dřevo)     | (Dlažba)     | (Laminát)      | POKOJ            |
| [0.365, 2.875]       | [1.875,2.875]| [3.000, 5.525] | (Laminát)        |
+----------------------+              |                |                  |
| 1.09 TECH. MÍSTNOST  |              |                |                  |
| [0.365, 1.750]       |              |                |                  |
+----------------------+              |                |                  |
| 1.08 WC              |              |                |                  |
| [0.365, 1.750]       |              |                |                  |
+-------------------------------------+                |                  |
| 1.07 POKOJ (Zkosený roh 45°)        | 1.02 CHODBA    |                  |
| [0.365, 4.395 x 3.975, 6.975]       | [4.520, 6.100] |                  |
+-------------------------------------+                +------------------+
| 1.06 POKOJ (Tvar L)                 | 1.01 ZÁDVĚŘÍ   | 1.05 POKOJ       |
| [0.365, 4.395 x 0.365, 3.850]       | (Dlažba)       | (Laminát)        |
|                                     | [3.775, 6.100] | [6.225, 9.635]   |
+-------------------------------------------------------------------------+ Y = 0.000 m
X = 0.000 m                                                    X = 10.000 m
```

### 2.1 Přesné souřadnice podlahových polygonů:
1. **1.01 ZÁDVĚŘÍ** ($5.46\text{ m}^2$, keramická dlažba `koupelna`):
   - Box: $X \in [3.775, 6.100]$, $Y \in [0.365, 2.350]$, $Z \in [0.000, 0.015]$.
2. **1.02 CHODBA** ($7.78\text{ m}^2$, laminát `laminate_floor_02.001`):
   - Polygon: $(4.520, 2.475) \to (6.100, 2.475) \to (6.100, 4.850) \to (4.520, 6.182)$.
3. **1.03 KUCHYNĚ** ($11.45\text{ m}^2$, laminát):
   - Box: $X \in [3.000, 5.525]$, $Y \in [7.100, 11.635]$, $Z \in [0.000, 0.015]$.
4. **1.04 OBÝVACÍ POKOJ** ($33.68\text{ m}^2$, laminát):
   - Severní část: Box $X \in [5.525, 9.635]$, $Y \in [7.100, 11.635]$.
   - Jižní část: Polygon $(4.520, 6.182) \to (6.100, 4.850) \to (9.635, 4.850) \to (9.635, 7.100) \to (3.000, 7.100) \to (3.602, 7.100)$.
   - Krbové těleso: Původní krb $1300\text{ mm}$ odstraněn, stěna plynule navazuje na pokoj 1.07.
5. **1.05 POKOJ** ($14.87\text{ m}^2$, laminát):
   - Box: $X \in [6.225, 9.635]$, $Y \in [0.365, 4.725]$, $Z \in [0.000, 0.015]$.
6. **1.06 POKOJ** ($12.18\text{ m}^2$, laminát):
   - Půdorys tvaru L: $X \in [0.365, 4.395]$, $Y \in [0.365, 3.850]$, výkus pro vestavěnou skříň zádveří.
7. **1.07 POKOJ** ($12.42\text{ m}^2$, laminát):
   - Polygon se zkoseným rohem $45^\circ$: $(0.365, 3.975) \to (4.395, 3.975) \to (4.395, 6.057) \to (3.477, 6.975) \to (0.365, 6.975)$.
8. **1.08 WC** ($1.91\text{ m}^2$, keramická dlažba `koupelna`):
   - Box: $X \in [0.365, 1.750]$, $Y \in [7.100, 8.485]$, $Z \in [0.000, 0.015]$. Obklad stěn do výšky $Z = 1.150\text{ m}$.
9. **1.09 TECHNICKÁ MÍSTNOST** ($2.02\text{ m}^2$, keramická dlažba `koupelna`):
   - Box: $X \in [0.365, 1.750]$, $Y \in [8.610, 9.995]$, $Z \in [0.000, 0.015]$.
10. **1.10 KOUPELNA** ($7.23\text{ m}^2$, keramická dlažba `koupelna`):
    - Box: $X \in [0.365, 2.875]$, $Y \in [10.120, 11.635]$, $Z \in [0.000, 0.015]$.
    - Sprchový kout: Dřevěná protiskluzová rohož `Mat_Shower_Wood` na $Z \in [0.015, 0.035\text{ m}]$.
11. **1.11 CHODBA** ($4.54\text{ m}^2$, keramická dlažba `koupelna`):
    - Box: $X \in [1.875, 2.875]$, $Y \in [7.100, 11.635]$, $Z \in [0.000, 0.015]$.

---

## 3. Standard Okenních Žaluzií

Všechna obytná okna mají jednotné černé horizontální žaluzie splňující projektový standard:

| Místnost / Pozice | Typ žaluzie | Šířka ($m$) | Výškový rozsah $Z$ ($m$) | Materiál |
| :--- | :--- | :--- | :--- | :--- |
| **1.03 Kuchyně (sever)** | Jednokřídlá horizontální | $1.500$ | $1.250 \to 2.250$ | `Mat_Kitchen_Black_Metal` |
| **1.04 Obývací pokoj (terasa)**| Dvě samostatná křídla (levé + pravé) | $2 \times 1.250$ | $0.120 \to 2.180$ | `Mat_Kitchen_Black_Metal` |
| **1.04 Obývací pokoj (východ)**| Dvoukřídlá horizontální | $2.000$ | $0.900 \to 2.250$ | `Mat_Kitchen_Black_Metal` |
| **1.05 Ložnice (jih)** | Dvoukřídlá horizontální | $2.000$ | $0.900 \to 2.250$ | `Mat_Kitchen_Black_Metal` |
| **1.06 Dětský pokoj (jih)** | Dvoukřídlá horizontální | $2.000$ | $0.900 \to 2.250$ | `Mat_Kitchen_Black_Metal` |
| **1.07 Pracovna (západ)** | Dvoukřídlá horizontální | $2.000$ | $0.900 \to 2.250$ | `Mat_Kitchen_Black_Metal` |

- **Konstrukce žaluzie**:
  - Horní krycí kazeta ($60 \times 60\,\text{mm}$)
  - Horizontální lamely (rozteč $50\text{--}55\,\text{mm}$, náklon $28^\circ$)
  - Spodní zatěžovací lišta
  - Boční napínací vodící lanka podél rámů

---

## 4. Standard Dřevodekoru (Kronospan K003 Gold Craft Oak)

Jednotný prémiový dekor dubu `Mat_Kronospan_K003_Gold_Craft_Oak` je aplikován na všechny dřevěné prvky v obytném prostoru:

| Prvek | Místnost | Rozměry ($m$) | Povrchový finiš |
| :--- | :--- | :--- | :--- |
| **Jídelní stůl** | 1.04 Obývací pokoj | $1.800 \times 0.900 \times 0.760$ | Deska K003 + černé kovové podnoží |
| **TV konzole (nízká)** | 1.04 Obývací pokoj | $2.400 \times 0.450 \times 0.420$ | K003 korpus a čela zásuvek |
| **Konferenční stolek** | 1.04 Obývací pokoj | $1.100 \times 0.600 \times 0.450$ | Masivní deska K003 |
| **Prosklená vitrína** | 1.04 Obývací pokoj | $0.900 \times 0.400 \times 1.600$ | K003 rám + čiré bezpečnostní sklo |
| **Zrcadlová police** | 1.04 Obývací pokoj | $1.200 \times 0.200 \times 0.040$ | K003 konzolová police |
| **Šatní komoda** | 1.05 Ložnice | $1.400 \times 0.450 \times 0.850$ | K003 korpus |
| **Kallax policový díl**| 1.06 Dětský pokoj | $1.470 \times 0.390 \times 1.470$ | K003 otevřené police $4 \times 4$ |

---

## 5. Zpevněné Plochy, Terasa a Exteriér

### 5.1 Výškové uspořádání
- Horní úroveň interiérové podlahy: $Z = 0.015\text{ m}$.
- Základová deska domu: $Z = -0.200 \to 0.000\text{ m}$.
- Venkovní zpevněné plochy (pochozí vrstva): $Z = 0.000\text{ m}$.

### 5.2 Zóny zpevněných ploch
1. **Přední příjezdová cesta a stání**:
   - Rozměry: Šířka $6.000\text{ m}$, protažení na jih do $Y = -22.000\text{ m}$ ($X \in [2.19, 8.19]$, $Y \in [-22.0, 0.0]$).
   - Materiál: Betonová zámková dlažba `Paving Stones` s UV mapováním 1:1 ke skutečným metrům (zajišťuje dokonale jednotnou velikost dlaždic bez deformace) a betonovými obrubníky `Garden_Curbs` po obou stranách.
2. **Zahradní terasa**:
   - Rozměry: Šířka $5.000\text{ m}$, hloubka $6.000\text{ m}$ ($X \in [5.00, 10.00]$, $Y \in [12.0, 18.0]$).
   - Dilatační spára a zapuštění pod HS portálem na $Z = -0.070\text{ m}$.
3. **Okapový chodník a kačírek**:
   - Drenážní kačírek podél obvodu celého domu šířky $0.500\text{ m}$.
   - Zahradní obrubníky oddělující travnatou plochu.
4. **Zahrada a trávník (`Lawn_Ground`)**:
   - Travnatá plocha $55.0 \times 55.0\text{ m}$ ($X \in [-25.0, 30.0]$, $Y \in [-25.0, 30.0]$ na $Z = -0.025\text{ m}$), pokrývající bez mezer kompletní 4K zorné pole kamery bez použití alpha fade (plné krytí Alpha = 1.0).
5. **Robotická sekačka Mammotion Yuka 2000**:
   - Umístění: Severní zahrada u stěny technické místnosti ($X \approx 0.60\text{ m}$, $Y \approx 12.30\text{ m}$).
   - Betonová podesta tl. $6\text{ cm}$ se zastřešenou nabíjecí stanicí (originální garáž Yuka).

---

## 6. Vozidlo: Škoda Scala Monte Carlo 2025

Vozidlo je sestaveno z oficiální CAD geometrie Škoda Auto a přesně zaparkováno na příjezdové cestě:

### 6.1 Pozice a orientace
- **Root objekt**: `Skoda_Scala_MonteCarlo_Root`
- **Souřadnice**: $(5.250, -3.500, 0.000)$
- **Rotace**: $\text{Euler}(0.0^\circ, 0.0^\circ, 0.0^\circ)$ (čelo vozu směřuje na jih)
- **Výšková poloha karoserie**: $Z = 0.700\text{ m}$ (reálná světlá výška $14\text{ cm}$, lem blatníku nad pneu $55\text{ mm}$)
- **Měřítko (CAD scale)**: $4.362 / 197.308 \approx 0.022107568$

### 6.2 Kola 17" Kajam Monte Carlo
- **Souřadnice os (středy)**:
  - Přední levé: $(-0.680, -1.300, 0.301)$
  - Přední pravé: $(+0.680, -1.300, 0.301)$
  - Zadní levé: $(-0.680, +1.300, 0.301)$
  - Zadní pravé: $(+0.680, +1.300, 0.301)$
- **Poloměr pneumatiky**: $R = 0.301\text{ m}$ (spodní bod pneu se přesně dotýká dlažby na $Z = 0.000\text{ m}$)
- **Materiály kola**:
  - `Mat_Scala_Silver_Alloy`: Vnější broušený obvodový lem ($r > 9.6\,\text{mm}$) a středový kruhový emblém Škoda ($r < 2.5\,\text{mm}$)
  - `Mat_Scala_Wheel_Black`: 5 aerodynamických lamel, vnitřní kapsy a barel disku
  - `Mat_Scala_Tyre_Rubber`: Dezén a bočnice pneumatiky
  - `Mat_Scala_Brake_Steel` & `Mat_Scala_Brake_Caliper`: Ocelový brzdový kotouč a červený brzdový třmen

### 6.3 Povrchy a zasklení
- `Mat_Scala_Velvet_Red`: Metalický červený lak karoserie (`Metallic 0.86`, `Roughness 0.14`, `Clearcoat 1.0`).
- `Mat_Scala_Black_Magic`: Klavírní černá střecha, boční zrcátka, B-sloupky, maska chladiče, spodní sání, stěrače a zadní difuzor.
- `Mat_Scala_Glass_Clear`: Čelní sklo a okna předních dveří ($Y < 0.075\text{ m}$, $Z \ge 0.215\text{ m}$).
- `Mat_Scala_Glass_Sunset_Privacy`: Tmavé tónování privacy glass na oknech zadních dveří, pevných oknech v C-sloupku nad nádrží ($0.185 \le Y \le 1.46\text{ m}$) a pátých dveřích kufru.
- `Mat_Scala_License_Plate`: Autentická česká registrační značka `1AH U743` s plastovou podložkou vpředu ($Y = -1.985$) i vzadu ($Y = 1.935$).

---

## 7. Světelný Plán (Podle výkresu `svetla 2022.jpg`)

Všechna svítidla jsou přesně umístěna ve 3D prostoru na výšce stropních bodovek $Z = 2.400\text{ m}$:

| Svítidlo | Typ | Souřadnice $(X, Y, Z)$ | Výkon ($W$) | Barva (RGB) | Poloměr ($m$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Light_1.01_Zadveri_V` | POINT | $(5.20, 1.265, 2.40)$ | 35 W | $(1.0, 0.95, 0.88)$ | 0.175 m |
| `Light_1.02_Chodba_V` | POINT | $(5.31, 3.700, 2.40)$ | 35 W | $(1.0, 0.95, 0.88)$ | 0.175 m |
| `Light_1.03_Kuchyne_V1` | POINT | $(4.30, 10.335, 2.40)$ | 40 W | $(1.0, 0.96, 0.90)$ | 0.175 m |
| `Light_1.03_Kuchyne_V2` | POINT | $(4.30, 9.035, 2.40)$ | 40 W | $(1.0, 0.96, 0.90)$ | 0.175 m |
| `Light_1.04_Obyvaci_pokoj_V1_Dining`| POINT | $(6.50, 10.635, 2.40)$ | 45 W | $(1.0, 0.95, 0.88)$ | 0.175 m |
| `Light_1.04_Obyvaci_pokoj_V2_Patio1`| POINT | $(8.025, 10.435, 2.40)$| 45 W | $(1.0, 0.95, 0.88)$ | 0.175 m |
| `Light_1.04_Obyvaci_pokoj_V3_Patio2`| POINT | $(8.025, 9.235, 2.40)$ | 45 W | $(1.0, 0.95, 0.88)$ | 0.175 m |
| `Light_1.04_Obyvaci_pokoj_V4_Center`| POINT | $(8.025, 7.200, 2.40)$ | 55 W | $(1.0, 0.95, 0.88)$ | 0.175 m |
| `Light_1.04_Obyvaci_pokoj_V5_Angle` | POINT | $(5.00, 6.500, 2.40)$ | 40 W | $(1.0, 0.95, 0.88)$ | 0.175 m |
| `Light_1.05_Pokoj_V1_South` | POINT | $(8.435, 1.565, 2.40)$ | 40 W | $(1.0, 0.95, 0.88)$ | 0.175 m |
| `Light_1.05_Pokoj_V2_Center`| POINT | $(8.435, 2.765, 2.40)$ | 40 W | $(1.0, 0.95, 0.88)$ | 0.175 m |
| `Light_1.05_Pokoj_Spot_West`| POINT | $(7.075, 4.100, 2.40)$ | 30 W | $(1.0, 0.95, 0.88)$ | 0.120 m |
| `Light_1.05_Pokoj_Spot_East`| POINT | $(8.785, 4.100, 2.40)$ | 30 W | $(1.0, 0.95, 0.88)$ | 0.120 m |
| `Light_1.06_Pokoj_V1_South` | POINT | $(2.05, 1.565, 2.40)$ | 40 W | $(1.0, 0.95, 0.88)$ | 0.175 m |
| `Light_1.06_Pokoj_V2_North` | POINT | $(2.05, 2.850, 2.40)$ | 40 W | $(1.0, 0.95, 0.88)$ | 0.175 m |
| `Light_1.07_Pokoj_V1_West` | POINT | $(1.565, 5.475, 2.40)$ | 40 W | $(1.0, 0.95, 0.88)$ | 0.175 m |
| `Light_1.07_Pokoj_V2_East` | POINT | $(3.195, 5.475, 2.40)$ | 40 W | $(1.0, 0.95, 0.88)$ | 0.175 m |
| `Light_1.08_WC_M` | POINT | $(1.06, 7.600, 2.40)$ | 20 W | $(1.0, 0.95, 0.88)$ | 0.120 m |
| `Light_1.09_Technicka_mistnost_M` | POINT | $(1.06, 8.950, 2.40)$ | 25 W | $(1.0, 0.95, 0.88)$ | 0.120 m |
| `Light_1.10_Koupelna_Vplus` | POINT | $(1.62, 10.600, 2.40)$| 50 W | $(1.0, 0.97, 0.92)$ | 0.225 m |
| `Light_1.11_Chodba_M1_Bath` | POINT | $(2.375, 9.200, 2.40)$ | 25 W | $(1.0, 0.95, 0.88)$ | 0.120 m |
| `Light_1.11_Chodba_M2_WC` | POINT | $(2.375, 7.650, 2.40)$ | 25 W | $(1.0, 0.95, 0.88)$ | 0.120 m |
| **Všechna světla (interiér i exteriér)** | AREA / SPOT / SUN | Dle rozpisu místností | Kalibrováno | `RGB (1.0, 1.0, 1.0)` pure white `#FFFFFF` | Bez barevného zkreslení |
| **Slunce (Sun_Fill)** | SUN | $(15.0, -10.0, 25.0)$ | 2.0 W | `RGB (1.0, 1.0, 1.0)` `#FFFFFF` | Rotace $50^\circ, 20^\circ, -35^\circ$ |

---

## 8. Kamera a Vykreslovací Parametry (Isometric View)

- **Objekt**: `Isometric_Camera`
- **Typ**: `PERSP` (perspektivní kamera)
- **Ohnisková vzdálenost (Lens)**: `50.0 mm` (senzor `50.0 mm`)
- **Pozice kamery**: `[14.794, 11.014, 15.908]`
- **Rotace kamery**: `[34.6°, 0.0°, 117.6°]` (Euler `XYZ`: `[0.6039, -0.0000, 2.0525]`)
- **Rozlišení scény**: `3840 × 2160` (100% 4K UHD, poměr stran 16:9)
- **Film Transparent**: `True` (zapnuto)
- **Engine**: Cycles (GPU Compute, OpenImageDenoise)

---

## 9. Plná Reprodukovatelnost a Automatizace

### 9.1 Vygenerování 4 master půdorysů:
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b "dum_pudorys.blend" -P "render_exact_user_modes.py"
```

### 9.2 Sestavení skleněné sprchové zástěny:
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b "dum_pudorys.blend" -P "build_shower_screen.py"
```

### 9.3 Sestavení modelu vozu z CAD podkladů:
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b "dum_pudorys.blend" -P "scratch/build_final_scala.py"
```

### 9.4 Vytvoření záložního archivu projektu:
```powershell
python "create_backup_archive.py"
```
