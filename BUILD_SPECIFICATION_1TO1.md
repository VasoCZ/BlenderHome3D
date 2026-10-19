# Kompletní 1:1 Stavební a Modelovací Specifikace Projektu BlenderHome3D

Tento dokument představuje **deterministickou, absolutně přesnou technickou specifikaci** rodinného domu pro 3D software **Blender 5.2+**. 
Podle těchto parametrů a vzorců lze kdykoliv postavit **1:1 identický model** na první pokus bez jakýchkoliv odchylek či nejasností.

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
| **Nášlapná vrstva podlah** | Tloušťka $0.015\text{ m}$ ($15\text{ mm}$) | $0.000 \to 0.015\text{ m}$ | Dlažba / plovoucí laminát |
| **Základová deska & zpevněné plochy** | Tloušťka $0.200\text{ m}$ ($20\text{ cm}$) | $-0.200 \to 0.000\text{ m}$ | Monolitický beton + dlažba |
| **Střešní atika / římsa (Soffit)** | Šířka profilu $0.500\text{ m}$ | $2.420 \to 2.500\text{ m}$ | Vnější obvod $11.0 \times 13.0\text{ m}$ |

---

## 2. Podrobný Rozpis Místností (Room Schedule 1.01 až 1.11)

Všechny místnosti odpovídají oficiálnímu stavebnímu výkresu `Půdorys-aktualní 27.10.2020.png`:

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
| 1.06 POKOJ (Tvar L)                 | 1.01 ZÁDVEŘÍ   | 1.05 POKOJ       |
| [0.365, 4.395 x 0.365, 3.850]       | (Dlažba)       | (Laminát)        |
|                                     | [3.775, 6.100] | [6.225, 9.635]   |
+-------------------------------------------------------------------------+ Y = 0.000 m
X = 0.000 m                                                    X = 10.000 m
```

### Přesné souřadnice podlahových polygonů:
1. **1.01 ZÁDVEŘÍ** ($5.46\text{ m}^2$, keramická dlažba):
   - Box: $X \in [3.775, 6.100]$, $Y \in [0.365, 2.350]$, $Z \in [0.000, 0.015]$.
2. **1.02 CHODBA** ($7.78\text{ m}^2$, laminát):
   - Polygon: $(4.520, 2.475) \to (6.100, 2.475) \to (6.100, 4.850) \to (4.520, 6.182)$.
3. **1.03 KUCHYNĚ** ($11.45\text{ m}^2$, laminát):
   - Box: $X \in [3.000, 5.525]$, $Y \in [7.100, 11.635]$, $Z \in [0.000, 0.015]$.
4. **1.04 OBÝVACÍ POKOJ** ($33.68\text{ m}^2$, laminát):
   - Severní část: Box $X \in [5.525, 9.635]$, $Y \in [7.100, 11.635]$.
   - Jižní část: Polygon $(4.520, 6.182) \to (6.100, 4.850) \to (9.635, 4.850) \to (9.635, 7.100) \to (3.000, 7.100) \to (3.602, 7.100)$.
5. **1.05 POKOJ** ($14.87\text{ m}^2$, laminát):
   - Box: $X \in [6.225, 9.635]$, $Y \in [0.365, 4.725]$, $Z \in [0.000, 0.015]$.
6. **1.06 POKOJ** ($13.37\text{ m}^2$, laminát - půdorys L):
   - Polygon: $(0.365, 0.365) \to (3.650, 0.365) \to (3.650, 2.475) \to (4.395, 2.475) \to (4.395, 3.850) \to (0.365, 3.850)$.
7. **1.07 POKOJ** ($11.95\text{ m}^2$, laminát - zkosený SV roh $45^\circ$):
   - Polygon: $(0.365, 3.975) \to (4.395, 3.975) \to (4.395, 6.130) \to (3.550, 6.975) \to (0.365, 6.975)$.
8. **1.08 WC** ($1.38\text{ m}^2$, keramická dlažba):
   - Box: $X \in [0.365, 1.750]$, $Y \in [7.100, 8.100]$, $Z \in [0.000, 0.015]$.
9. **1.09 TECHNICKÁ MÍSTNOST** ($2.15\text{ m}^2$, keramická dlažba):
   - Box: $X \in [0.365, 1.750]$, $Y \in [8.225, 9.775]$, $Z \in [0.000, 0.015]$.
10. **1.10 KOUPELNA** ($4.35\text{ m}^2$, keramická dlažba):
    - Box: $X \in [0.365, 2.875]$, $Y \in [9.900, 11.635]$, $Z \in [0.000, 0.015]$.
11. **1.11 CHODBA** ($2.68\text{ m}^2$, keramická dlažba):
    - Box: $X \in [1.875, 2.875]$, $Y \in [7.100, 9.775]$, $Z \in [0.000, 0.015]$.

---

## 3. Otvory: Okna, Dveře a Konstrukční Detaily

### 3.1 Vnější fasádní otvory
| Otvor | Místnost | Fasáda | Souřadnice osy / rozpětí | Parapet ($Z$) | Nadpraží / Výška | Překlad ($Z$) | Použitý model / Asset |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **W1** | 1.06 Pokoj | Jižní | $X \in [1.300, 2.800]\text{ m}$ (šířka $1.50\text{ m}$) | $0.850\text{ m}$ | $2.250\text{ m}$ ($H = 1.40\text{ m}$) | $2.250 \to 2.500\text{ m}$ | Asset 2: `dfc43034-0e61-4ed3-9ebd-4d703fc152a2` (dvoukřídlé) |
| **P1 Vchod** | 1.01 Zádveří | Jižní | $X \in [4.640, 5.740]\text{ m}$ (šířka $1.10\text{ m}$) | $0.000\text{ m}$ | $2.050\text{ m}$ ($H = 2.05\text{ m}$) | $2.050 \to 2.500\text{ m}$ | `entrance_door.blend` (rám `ram` + křídlo `dvere`) |
| **W1** | 1.05 Pokoj | Jižní | $X \in [7.200, 8.700]\text{ m}$ (šířka $1.50\text{ m}$) | $0.850\text{ m}$ | $2.250\text{ m}$ ($H = 1.40\text{ m}$) | $2.250 \to 2.500\text{ m}$ | Asset 2: `dfc43034-0e61-4ed3-9ebd-4d703fc152a2` (dvoukřídlé) |
| **W2 Jih** | 1.04 Obývací | Východní | $Y \in [5.900, 7.640]\text{ m}$ (šířka $1.74\text{ m}$) | $0.850\text{ m}$ | $2.250\text{ m}$ ($H = 1.40\text{ m}$) | $2.250 \to 2.500\text{ m}$ | Asset 1: `08d106b3-58d9-42d0-ae99-bce92d0b2667` (jednokřídlé) |
| **W2 Sever** | 1.04 Obývací | Východní | $Y \in [8.780, 10.520]\text{ m}$ (šířka $1.74\text{ m}$) | $0.850\text{ m}$ | $2.250\text{ m}$ ($H = 1.40\text{ m}$) | $2.250 \to 2.500\text{ m}$ | Asset 1: `08d106b3-58d9-42d0-ae99-bce92d0b2667` (jednokřídlé) |
| **W5** | 1.10 Koupelna | Severní | $X \in [1.120, 2.120]\text{ m}$ (šířka $1.00\text{ m}$) | $1.250\text{ m}$ | $2.250\text{ m}$ ($H = 1.00\text{ m}$) | $2.250 \to 2.500\text{ m}$ | Asset 1: `08d106b3-58d9-42d0-ae99-bce92d0b2667` (jednokřídlé) |
| **W4** | 1.03 Ložnice | Severní | $X \in [3.660, 5.400]\text{ m}$ (šířka $1.74\text{ m}$) | $0.850\text{ m}$ | $2.250\text{ m}$ ($H = 1.40\text{ m}$) | $2.250 \to 2.500\text{ m}$ | Asset 1: `08d106b3-58d9-42d0-ae99-bce92d0b2667` (jednokřídlé) |
| **Francouzské 3** | 1.04 Obývací | Severní | $X \in [7.125, 8.925]\text{ m}$ (šířka $1.80\text{ m}$) | $0.000\text{ m}$ | $2.150\text{ m}$ ($H = 2.15\text{ m}$) | $2.150 \to 2.500\text{ m}$ | `japanese_sliding_window.blend` (posuvné sítě a křídla) |
| **W05** | 1.07 Pokoj | Západní | $Y \in [4.725, 6.225]\text{ m}$ (šířka $1.50\text{ m}$) | $0.850\text{ m}$ | $2.250\text{ m}$ ($H = 1.40\text{ m}$) | $2.250 \to 2.500\text{ m}$ | Asset 2: `dfc43034-0e61-4ed3-9ebd-4d703fc152a2` (dvoukřídlé) |
| **W6 Jih** | 1.08 WC | Západní | $Y \in [7.200, 8.000]\text{ m}$ (šířka $0.80\text{ m}$) | $1.250\text{ m}$ | $2.250\text{ m}$ ($H = 1.00\text{ m}$) | $2.250 \to 2.500\text{ m}$ | Asset 1: `08d106b3-58d9-42d0-ae99-bce92d0b2667` (jednokřídlé) |
| **W6 Sever** | 1.09 Tech. místnost| Západní | $Y \in [8.375, 9.175]\text{ m}$ (šířka $0.80\text{ m}$) | $1.250\text{ m}$ | $2.250\text{ m}$ ($H = 1.00\text{ m}$) | $2.250 \to 2.500\text{ m}$ | Asset 1: `08d106b3-58d9-42d0-ae99-bce92d0b2667` (jednokřídlé) |

### 3.1.1 Okenní modely a parapetní desky (`Window_Models`, `Window_Sills`)
Okenní otvory jsou osazeny reálnými 3D modely oken s tmavým antracitovým PVC profilem a architektonickými parapety:
1. **Jednokřídlé PVC okno (Asset 1 - `08d106b3-58d9-42d0-ae99-bce92d0b2667`)**:
   - Tmavý PVC rám (`PVC`, `#141414`), čiré izolační sklo (`Glass`, transmission 1.0, roughness 0.0), distanční rámeček (`Rim_Glass`) a těsnění (`Rubber`).
   - Použito pro místnosti: **1.03** (ložnice), **1.04** (obývací pokoj – obě východní okna), **1.08** (WC), **1.09** (technická místnost), **1.10** (koupelna).
2. **Dvoukřídlé PVC okno se sloupkem (Asset 2 - `dfc43034-0e61-4ed3-9ebd-4d703fc152a2`)**:
   - Dvojité zasklení se středovým sloupkem, tmavý PVC profil.
   - Použito pro místnosti: **1.05** (pokoj jih), **1.06** (pokoj jih), **1.07** (pokoj západ).
3. **Plné stěnové překlady (`Exterior_Walls`)**:
   - Všechny okenní otvory jsou shora uzavřeny plným zdivem překladu v rozsahu $Z \in [2.250, 2.500]\text{ m}$ (tloušťka překladu $25\text{ cm}$).
   - Horní hrana obvodových stěn $Z = 2.500\text{ m}$ je po celém obvodu $360^\circ$ spojitá a souvislá; střešní římsa (`Roof_Soffit_Cornice`, $Z \in [2.420, 2.500]\text{ m}$) sedí po celém obvodu na zdivu.
4. **Venkovní parapet s okapovým nosem (Exterior Sill with Downward Drip Nose)**:
   - **Materiál**: `Mat_Roof_Soffit` (antracitový plech RAL 7016 ladící s atikou i rámy).
   - **Vodorovná deska**: Tloušťka $20\text{ mm}$ ($Z \in [Z_{\text{sill}} - 0.020, Z_{\text{sill}}]\text{ m}$), vyložená $35\text{ mm}$ před vnější líc fasády s bočními lemy ($20\text{ mm}$ uši).
   - **Převislý okapový nos (drip nose)**: Spuštěný o $20\text{ mm}$ dolů ($Z \in [Z_{\text{sill}} - 0.040, Z_{\text{sill}} - 0.020]\text{ m}$), čelní pohledová výška $40\text{ mm}$.
5. **Vnitřní parapetní deska s převislým nosem (Interior Sill with Downward Nose)**:
   - **Materiál**: `Mat_Roof_Soffit` (antracit).
   - **Horizontální deska**: Tloušťka $25\text{ mm}$ ($Z \in [Z_{\text{sill}} - 0.025, Z_{\text{sill}}]\text{ m}$), vyložená $25\text{ mm}$ do interiéru s bočními uchy $20\text{ mm}$.
   - **Převislý nos (apron nose)**: Spuštěný o $20\text{ mm}$ dolů.

### 3.2 Konstrukční usazení vchodových dveří a eliminace mezer
Vchodové dveře sestávají z prvků:
- `ram`: Vnější hliníkový rám o rozměrech: šířka $1.100\text{ m}$, hloubka $0.138\text{ m}$, výška upravena přesně na $2.050\text{ m}$.
- `dvere`: Dveřní křídlo (světlost $2.00\text{ m}$) se zasklením a klikou `dvere.001` (výška kliky $1.05\text{ m}$).
- **Boční pera a překlad**:
  - Levé pero: $X \in [4.640, 4.705]\text{ m}$, $Y \in [0.015, 0.123]\text{ m}$, $Z \in [0.000, 2.050]\text{ m}$.
  - Pravé pero: $X \in [5.675, 5.740]\text{ m}$, $Y \in [0.015, 0.123]\text{ m}$, $Z \in [0.000, 2.050]\text{ m}$.
  - Horní překlad: $X \in [4.640, 5.740]\text{ m}$, $Y \in [0.000, 0.365]\text{ m}$, $Z \in [2.050, 2.500]\text{ m}$.

### 3.3 Vnitřní dveřní otvory, překlady a obložkové zárubně
Všech 8 vnitřních dveřních otvorů má standardní reálnou stavební světlost výšky $2.000\text{ m}$:
- **Stěnové překlady (`Interior_Walls`)**: Plné zdivo překladu v rozsahu $Z \in [2.000, 2.500]\text{ m}$ (výška překladu $50\text{ cm}$) sjednocuje horní hranu všech vnitřních příček na $Z = 2.500\text{ m}$.
- **Překlad koupelny 1.10**: Z vnitřní strany koupelny (+Y líc) nese keramický obklad `koupelna stena` (`sokl chodba.001`).
- **Obložkové zárubně (`Interior_Door_Frames`)**:
  - Svislé boční obložky z obou stran stěny: $Z \in [0.000, 2.050]\text{ m}$.
  - Horní vodorovná obložka: $Z \in [2.000, 2.050]\text{ m}$.
  - Šířka obložky: $50\text{ mm}$, hloubka přesahu $15\text{ mm}$.
  - Materiál: `Mat_Roof_Soffit` (antracit RAL 7016).

| Spojení místností | Směr zdi | Souřadnice otvoru | Šířka otvoru | Světlá výška |
| :--- | :--- | :--- | :--- | :--- |
| **1.01 Zádveří $\to$ 1.02 Chodba** | Horizontální | $X \in [4.700, 5.500]\text{ m}$, $Y \in [2.350, 2.475]\text{ m}$ | $0.800\text{ m}$ | $2.000\text{ m}$ |
| **1.02 Chodba $\to$ 1.05 Pokoj** | Vertikální | $Y \in [2.800, 3.600]\text{ m}$, $X \in [6.100, 6.225]\text{ m}$ | $0.800\text{ m}$ | $2.000\text{ m}$ |
| **1.02 Chodba $\to$ 1.06 Pokoj** | Vertikální | $Y \in [2.700, 3.500]\text{ m}$, $X \in [4.395, 4.520]\text{ m}$ | $0.800\text{ m}$ | $2.000\text{ m}$ |
| **1.02 Chodba $\to$ 1.07 Pokoj** | Vertikální | $Y \in [4.800, 5.600]\text{ m}$, $X \in [4.395, 4.520]\text{ m}$ | $0.800\text{ m}$ | $2.000\text{ m}$ |
| **1.11 Chodba $\to$ 1.10 Koupelna** | Horizontální | $X \in [2.050, 2.750]\text{ m}$, $Y \in [9.775, 9.900]\text{ m}$ | $0.700\text{ m}$ | $2.000\text{ m}$ |
| **1.11 Chodba $\to$ 1.08 WC** | Vertikální | $Y \in [7.250, 7.950]\text{ m}$, $X \in [1.750, 1.875]\text{ m}$ | $0.700\text{ m}$ | $2.000\text{ m}$ |
| **1.11 Chodba $\to$ 1.09 Tech** | Vertikální | $Y \in [8.550, 9.250]\text{ m}$, $X \in [1.750, 1.875]\text{ m}$ | $0.700\text{ m}$ | $2.000\text{ m}$ |
| **1.04 Obývací $\to$ 1.11 Chodba** | Vertikální | $Y \in [7.200, 8.000]\text{ m}$, $X \in [2.875, 3.000]\text{ m}$ | $0.800\text{ m}$ | $2.000\text{ m}$ |

### 3.4 Zárubňové prahy a podlahové přechody (`Floor_Threshold_*`)
Pro zamezení prosvítání venkovní dlažby pod příčkami domu jsou ve všech dveřních otvorech vytvořeny nášlapné vrstvy podlah ($Z \in [0.000, 0.015]\text{ m}$):
1. **Laminát $\to$ Laminát** (např. 1.02 $\to$ 1.05, 1.06, 1.07):
   - Souvislá vrstva laminátu s identickým světovým UV mapováním (`UVMap` i `automap`), které plynule navazuje na kresbu dřeva v sousedních místnostech.
2. **Dlažba $\to$ Dlažba** (1.11 $\to$ 1.08, 1.09, 1.10):
   - Souvislá keramická dlažba s UV mapováním navazujícím na dlažbu chodby.
3. **Dlažba $\to$ Laminát** (1.01 $\to$ 1.02 a 1.04 $\to$ 1.11):
   - Půlený práh (polovina dlažba, polovina laminát) s anodizovanou hliníkovou přechodovou lištou (`Mat_Transition_Strip`, šířka $20\text{ mm}$, výška $+1.5\text{ mm}$ nad podlahu).
4. **Vchod a terasa**:
   - Vnitřní líc vchodových dveří ($Y \in [0.138, 0.365]$) kryt dlažbou zádveří.
   - Vnitřní líc terasového okna ($Y \in [11.635, 11.710]$) kryt laminátem obývacího pokoje.

### 3.5 Terasové posuvné dveře (Japanese Sliding Window with Screen)
- **Umístění**: Severní stěna obývacího pokoje 1.04, $X \in [7.125, 8.925]\text{ m}$, $Y \in [11.710, 11.950]\text{ m}$.
- **Výška**: Škálováno na plnou výšku $Z = 2.150\text{ m}$ ($H = 2.15\text{ m}$).
- **Horní překlad**: Zdivo nadpraží v `Exterior_Walls` v rozsahu $Z \in [2.150, 2.500]\text{ m}$ ($35\text{ cm}$ masivní stěnový překlad).

---

## 4. Základová Deska a Zpevněné Plochy (100% Ortogonální Quad Síť)

Síť objektu `Foundation_Slab` je vygenerována z unifikovaných řezů bez jediného šikmého nebo diagonálního polygonu (čisté čtyřúhelníky s pravými úhly $90^\circ$):

### 4.1 Řezy souřadnic
- **Osa $X$**: $[-1.20, 2.19, 5.00, 8.19, 10.00, 11.20]$
- **Osa $Y$**: $[-9.00, -1.20, 0.00, 12.00, 13.20, 18.00]$
- **Výška $Z$**: Horní povrch $Z = 0.000\text{ m}$, spodní hrana $Z = -0.200\text{ m}$ (tloušťka desky $20\text{ cm}$).

### 4.2 Zóny zpevněných ploch
1. **Okapový chodník**: Šířka $1.200\text{ m}$ kolem obvodu celého domu ($X \in [-1.2, 11.2]$, $Y \in [-1.2, 13.2]$).
2. **Přední příjezdová plocha**: Šířka $6.000\text{ m}$, délka $9.000\text{ m}$ ($X \in [2.19, 8.19]$, $Y \in [-9.0, 0.0]$), přesně symetricky vycentrovaná na vchodové dveře.
3. **Zadní terasa**: Šířka $5.000\text{ m}$, hloubka $6.000\text{ m}$ ($X \in [5.00, 10.00]$, $Y \in [12.0, 18.0]$), navazující na francouzské dveře obývacího pokoje.
4. **Materiál dlažby**: `Stone ground tile` / `Mat_Outdoor_Concrete_Paving` (antracitová betonová dlažba).

### 4.3 Tloušťka desky a zahradní obrubníky (`Garden_Curbs`)
1. **Reálná výška dlažby**: Modifikátor `Solidify` na objektu `Foundation_Slab` s tloušťkou $0.080\text{ m}$ ($8\text{ cm}$) orientovanou směrem dolů (`offset = -1.0`).
2. **Zahradní obrubníky (`Garden_Curbs`)**:
   - Šířka obrubníku: $0.080\text{ m}$ ($8\text{ cm}$).
   - Výška obrubníku: Spodní hrana $Z = -0.080\text{ m}$, horní hrana $Z = +0.035\text{ m}$ ($3.5\text{ cm}$ nad úroveň dlažby).
   - Lemuje všech 12 vnějších obvodových hran zpevněné plochy (příjezdová cesta, okapové chodníky, terasa).
   - Materiál: `Mat_Garden_Curb` (hladký tmavší vibrolisovaný beton `#1E2022`, roughness 0.65). Vytváří přirozené ohraničení pozemku s vrženým stínem.

---

## 5. Koupelna: Dva Materiály & Odstranění Bílých Spár

V koupelně (místnost 1.10) jsou stěny rozděleny na dva samostatné materiály:
- **Sprchový kout**: Dřevěný lamelový obklad (`Plank stena`)
- **Zbylé stěny**: Šedý velkoformátový obklad (`koupelna stena`)

### 5.1 Hranice přechodu materiálů
- **Západní obvodová stěna**:
  - Sprchový kout: $Y \in [9.900, 10.890]\text{ m}$ $\to$ `Plank stena` (vertikální plocha i horní řezová plocha $Z = 1.800\text{ m}$).
  - Koupelnový obklad: $Y \in [10.890, 11.635]\text{ m}$ $\to$ `koupelna stena`.
- **Jižní vnitřní příčka**:
  - Sprchový kout: $X \in [0.365, 1.368]\text{ m}$ $\to$ `Plank stena`.
  - Koupelnový obklad: $X \in [1.368, 2.050]\text{ m}$ a ostění $X \in [2.750, 2.875]\text{ m}$ $\to$ `koupelna stena`.
  - **Překlad dveří 1.11 -> 1.10**: Severní plocha překladu facing do koupelny ($X \in [2.050, 2.750]\text{ m}$, $Y = 9.900\text{ m}$, $Z \in [1.600, 1.800]\text{ m}$) a horní hrana ($Z = 1.800\text{ m}$) $\to$ `koupelna stena` / `Material` se spojitým UV mapováním navazujícím na okolní stěny.

### 5.2 Klíčová oprava vizuálních bugů (Bílé linky a trhliny na hranách)
Bílé linky na přechodu obkladů a horních hranách vznikaly ze dvou příčin:
1. **Displacement Socket ve shaderu**: Blendkit materiály měly zapojený Displacement socket do Material Output. V EEVEE/Cycles způsoboval mikroskopické posunutí vrcholů na hranici různých materiálů, což odhalovalo mezeru mezi sousedními polygony.
   - **Fix**: Úplné odpojení displacement nodu ve všech materiálech.
2. **Překrytí textury na horní hraně ($Z = 1.800\text{ m}$)**:
   - **Fix**: Horní plochy stěn mají přiřazeny stejné materiálové sloty a zarovnané UV mapování, takže horní řez stěny plynule navazuje na svislý obklad.

---

## 6. Světelný Plán (Podle výkresu `svetla 2022.jpg`)

Všechna světla jsou přesně umístěna ve 3D prostoru:

| Světlo | Typ | Souřadnice $(X, Y, Z)$ | Výkon ($W$) | Barva (RGB) | Průměr ($m$) |
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
| **Fasádní bodovky (Soffit 1 až 5)**| SPOT | $Z = 2.45\text{ m}$, kužel $50^\circ$| 20 W | $(1.0, 0.94, 0.82)$ | Směr dolů |
| **Terasa nástěnná světla** | POINT | $Z = 2.40\text{ m}$ (na fasádě)| 35 W | $(1.0, 0.94, 0.82)$ | 0.150 m |
| **Slunce (Sun_Fill)** | SUN | $(15.0, -10.0, 25.0)$ | 2.0 W | $(1.0, 0.98, 0.95)$ | Rotace $50^\circ, 20^\circ, -35^\circ$ |

---

## 7. Kamera a Vykreslovací Parametry (Isometric View)

- **Objekt**: `Isometric_Camera`
- **Typ**: `ORTHO` (ortografická izometrická kamera)
- **Ortho Scale**: `18.0` (dokonale rámuje půdorys domu i s chodníky a příjezdovou cestou při výšce stěn 2.5m)
- **Cílový bod (Target)**: $\vec{T} = (5.0, 6.0, 1.25)$ (střed hmoty domu)
- **Směrový vektor izometrie**: $\vec{D} = \frac{(-1.0, -1.0, \sqrt{2})}{\|\dots\|}$
- **Vzdálenost kamery**: $35.0\text{ m}$
- **Pozice kamery**: $\vec{T} + 35.0 \times \vec{D}$
- **Rotace**: `direction.to_track_quat('-Z', 'Y')`

---

## 8. Jednokroková Rekonstrukce Modelu (1:1 Build)

Model lze sestavit na první dobrou spuštěním jednoho jediného příkazu v terminálu:

```bash
blender --background --python build_complete_model.py
```

Skript provede:
1. Vyčištění scény od všech pozůstatků.
2. Vytvoření všech materiálů s přesnými barevnými hodnotami.
3. Vygenerování 100% ortogonální základové desky a dlažeb.
4. Vymodelování obvodových zdí se všemi stavebními otvory a začisťujícími prvky.
5. Vymodelování vnitřních příček všech 11 místností včetně zkosení koupelny pod $45^\circ$.
6. Vygenerování nášlapných vrstev podlah s dlažbami i lamináty.
7. Vytvoření střešní římsy (soffit cornice).
8. Importování/vygenerování přesné sestavy vchodových dveří.
9. Osazení všech 26 světelných zdrojů dle projektu elektroinstalace.
10. Nastavení izometrické kamery a uložení čistého souboru `dum_pudorys.blend` a náhledu `dum_pudorys_overview.png`.
