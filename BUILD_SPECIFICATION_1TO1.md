# Kompletní 1:1 Stavební a Modelovací Specifikace Projektu BlenderHome3D

Tento dokument představuje **deterministickou, absolutně přesnou technickou specifikaci** rodinného domu pro 3D software **Blender 5.2+**. 
Podle těchto parametrů a vzorců lze kdykoliv postavit **1:1 identický model** na první pokus bez jakýchkoliv odchylek či nejasností, včetně všech ručních i automatizovaných úprav.

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

### 2.1 Přesné souřadnice podlahových polygonů:
1. **1.01 ZÁDVEŘÍ** ($5.46\text{ m}^2$, keramická dlažba `koupelna`):
   - Box: $X \in [3.775, 6.100]$, $Y \in [0.365, 2.350]$, $Z \in [0.000, 0.015]$.
2. **1.02 CHODBA** ($7.78\text{ m}^2$, laminát `laminate_floor_02.001`):
   - Polygon: $(4.520, 2.475) \to (6.100, 2.475) \to (6.100, 4.850) \to (4.520, 6.182)$.
3. **1.03 KUCHYNĚ** ($11.45\text{ m}^2$, laminát):
   - Box: $X \in [3.000, 5.525]$, $Y \in [7.100, 11.635]$, $Z \in [0.000, 0.015]$.
4. **1.04 OBÝVACÍ POKOJ** ($33.68\text{ m}^2$, laminát):
   - Severní část: Box $X \in [5.525, 9.635]$, $Y \in [7.100, 11.635]$.
   - Jižní část: Polygon $(4.520, 6.182) \to (6.100, 4.850) \to (9.635, 4.850) \to (9.635, 7.100) \to (3.000, 7.100) \to (3.602, 7.100)$.
   - Krbové těleso: Původní krb $1300\text{ mm}$ vybourán a odstraněn, stěna za krbem plynule navazuje na pokoj 1.07.
5. **1.05 POKOJ** ($14.87\text{ m}^2$, laminát):
   - Box: $X \in [6.225, 9.635]$, $Y \in [0.365, 4.725]$, $Z \in [0.000, 0.015]$.
6. **1.06 POKOJ** ($13.37\text{ m}^2$, laminát - půdorys L):
   - Polygon: $(0.365, 0.365) \to (3.650, 0.365) \to (3.650, 2.475) \to (4.395, 2.475) \to (4.395, 3.850) \to (0.365, 3.850)$.
7. **1.07 POKOJ** ($11.95\text{ m}^2$, laminát - zkosený SV roh $45^\circ$):
   - Polygon: $(0.365, 3.975) \to (4.395, 3.975) \to (4.395, 6.130) \to (3.550, 6.975) \to (0.365, 6.975)$.
8. **1.08 WC** ($1.38\text{ m}^2$, keramická dlažba `koupelna`):
   - Box: $X \in [0.365, 1.750]$, $Y \in [7.100, 8.163]$, $Z \in [0.000, 0.015]$ (severní hrana dotažena k příčce pro eliminaci mezery).
9. **1.09 TECHNICKÁ MÍSTNOST** ($2.15\text{ m}^2$, keramická dlažba `koupelna`):
   - Box: $X \in [0.365, 1.750]$, $Y \in [8.288, 9.775]$, $Z \in [0.000, 0.015]$.
10. **1.10 KOUPELNA** ($4.35\text{ m}^2$, keramická dlažba `koupelna` + dřevěný rošt sprchy `Plank 1`):
    - Box: $X \in [0.365, 2.875]$, $Y \in [9.900, 11.635]$, $Z \in [0.000, 0.015]$.
11. **1.11 CHODBA** ($2.68\text{ m}^2$, keramická dlažba `koupelna`):
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
| **W5** | 1.10 Koupelna | Severní | $X \in [1.120, 2.120]\text{ m}$ (šířka $1.00\text{ m}$) | $1.750\text{ m}$ | $2.350\text{ m}$ ($H = 0.60\text{ m}$) | $2.350 \to 2.500\text{ m}$ | Asset 1: `08d106b3-58d9-42d0-ae99-bce92d0b2667` (jednokřídlé) |
| **W4** | 1.03 Kuchyně | Severní | $X \in [3.660, 5.400]\text{ m}$ (šířka $1.74\text{ m}$) | $0.850\text{ m}$ | $2.250\text{ m}$ ($H = 1.40\text{ m}$) | $2.250 \to 2.500\text{ m}$ | Asset 1: `08d106b3-58d9-42d0-ae99-bce92d0b2667` (jednokřídlé) |
| **Francouzské 3** | 1.04 Obývací | Severní | $X \in [7.125, 8.925]\text{ m}$ (šířka $1.80\text{ m}$) | $0.000\text{ m}$ | $2.150\text{ m}$ ($H = 2.15\text{ m}$) | $2.150 \to 2.500\text{ m}$ | `japanese_sliding_window.blend` (posuvné sítě a křídla) |
| **W05** | 1.07 Pokoj | Západní | $Y \in [4.725, 6.225]\text{ m}$ (šířka $1.50\text{ m}$) | $0.850\text{ m}$ | $2.250\text{ m}$ ($H = 1.40\text{ m}$) | $2.250 \to 2.500\text{ m}$ | Asset 2: `dfc43034-0e61-4ed3-9ebd-4d703fc152a2` (dvoukřídlé) |
| **W6 Jih** | 1.08 WC | Západní | $Y \in [7.200, 8.000]\text{ m}$ (šířka $0.80\text{ m}$) | $1.750\text{ m}$ | $2.350\text{ m}$ ($H = 0.60\text{ m}$) | $2.350 \to 2.500\text{ m}$ | Asset 1: `08d106b3-58d9-42d0-ae99-bce92d0b2667` (jednokřídlé) |
| **W6 Sever** | 1.09 Tech. místnost| Západní | $Y \in [8.375, 9.175]\text{ m}$ (šířka $0.80\text{ m}$) | $1.750\text{ m}$ | $2.350\text{ m}$ ($H = 0.60\text{ m}$) | $2.350 \to 2.500\text{ m}$ | Asset 1: `08d106b3-58d9-42d0-ae99-bce92d0b2667` (jednokřídlé) |

### 3.2 Okenní modely a parapetní desky (`Window_Models`, `Window_Sills`)
Okenní otvory jsou osazeny reálnými 3D modely oken s tmavým antracitovým PVC profilem a architektonickými parapety:
1. **Jednokřídlé PVC okno (Asset 1 - `08d106b3-58d9-42d0-ae99-bce92d0b2667`)**:
   - Tmavý PVC rám (`PVC`, `#141414`), čiré izolační sklo (`Glass`, transmission 1.0, roughness 0.0), distanční rámeček (`Rim_Glass`) a těsnění (`Rubber`).
   - Použito pro místnosti: **1.03** (kuchyně), **1.04** (obývací pokoj – obě východní okna), **1.08** (WC), **1.09** (technická místnost), **1.10** (koupelna).
   - Malá okna (1.08, 1.09, 1.10) jsou sjednocena na výšku parapetu $Z = 1.750\text{ m}$, výšku rámu $0.60\text{ m}$ a nadpraží $Z = 2.350\text{ m}$.
2. **Dvoukřídlé PVC okno se sloupkem (Asset 2 - `dfc43034-0e61-4ed3-9ebd-4d703fc152a2`)**:
   - Dvojité zasklení se středovým sloupkem, tmavý PVC profil.
   - Použito pro místnosti: **1.05** (pokoj jih), **1.06** (pokoj jih), **1.07** (pokoj západ).
3. **Plné stěnové překlady (`Exterior_Walls`)**:
   - Všechny okenní otvory jsou shora uzavřeny plným zdivem překladu v rozsahu $Z \in [Z_{\text{head}}, 2.500]\text{ m}$.
   - Horní hrana obvodových stěn $Z = 2.500\text{ m}$ je po celém obvodu $360^\circ$ spojitá a souvislá; střešní římsa (`Roof_Soffit_Cornice`, $Z \in [2.420, 2.500]\text{ m}$) sedí po celém obvodu na zdivu.
4. **Venkovní parapet s okapovým nosem (Exterior Sill with Downward Drip Nose)**:
   - **Materiál**: `Mat_Roof_Soffit` (antracitový plech RAL 7016 ladící s atikou i rámy).
   - **Vodorovná deska**: Tloušťka $20\text{ mm}$ ($Z \in [Z_{\text{sill}} - 0.020, Z_{\text{sill}}]\text{ m}$), vyložená $35\text{ mm}$ před vnější líc fasády s bočními lemy ($20\text{ mm}$ uši).
   - **Převislý okapový nos (drip nose)**: Spuštěný o $20\text{ mm}$ dolů ($Z \in [Z_{\text{sill}} - 0.040, Z_{\text{sill}} - 0.020]\text{ m}$), čelní pohledová výška $40\text{ mm}$.
5. **Vnitřní parapetní deska s převislým nosem (Interior Sill with Downward Nose)**:
   - **Materiál**: `Mat_Roof_Soffit` (antracit).
   - **Horizontální deska**: Tloušťka $25\text{ mm}$ ($Z \in [Z_{\text{sill}} - 0.025, Z_{\text{sill}}]\text{ m}$), vyložená $25\text{ mm}$ do interiéru s bočními uchy $20\text{ mm}$.
   - **Převislý nos (apron nose)**: Spuštěný o $20\text{ mm}$ dolů.

### 3.3 Vnitřní dveřní otvory, překlady a obložkové zárubně
Všech 8 vnitřních dveřních otvorů má standardní reálnou stavební světlost výšky $2.000\text{ m}$:
- **Stěnové překlady (`Interior_Walls`)**: Plné zdivo překladu v rozsahu $Z \in [2.000, 2.500]\text{ m}$ ($50\text{ cm}$) sjednocuje horní hranu všech vnitřních příček na $Z = 2.500\text{ m}$.
- **Překlad koupelny 1.10**: Z vnitřní strany koupelny (+Y líc) nese keramický obklad `sokl chodba.001`.
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
Pro dokonalou čistotu a zamezení prosvítání venkovní desky jsou prahy řešeny přesně podle požadavků investora:
1. **Laminát $\to$ Laminát** (1.02 $\to$ 1.05, 1.06, 1.07):
   - Souvislá vrstva laminátu s identickým světovým UV mapováním plynule navazující na kresbu dřeva.
2. **Dlažba $\to$ Dlažba** (1.11 $\to$ 1.08, 1.09, 1.10):
   - Souvislá šedá keramická dlažba `koupelna` v návaznosti na dlažbu chodby.
3. **Přechody Chodba $\to$ Zádveří / Kuchyň (101_102 a 104_111)**:
   - **Jednolitý masivní práh z výhradně šedé keramické dlažby (`koupelna`)** v celé šířce ostění dveří ($Z \in [0.000, 0.015]\text{ m}$). Původní tříprvkové dělení s přechodovými lištami bylo kompletně odstraněno.
4. **Práh terasy (`Floor_Threshold_Patio`)**:
   - Vnitřní líc terasových dveří kryt laminátem.
   - V půdorysu posuvných dveří ($X \in [7.125, 8.925]$, $Y \in [11.635, 11.850]$) jsou vrcholy desky `Foundation_Slab` **sníženy na $Z = -0.070\text{ m}$**, tedy pod úroveň spodní vodicí kolejnice HS portálu ($Z \ge -0.0624\text{ m}$). Zámková dlažba tak pod rámem ani v drážkách neprosvítá.

---

## 4. Spárořez, Soklíky a Obklady v Celém Domě

### 4.1 Matematicky deterministický spárořez
Aby spáry mezi kachličkami na zemi, na soklech i na celých stěnách navzájem přesně lícovaly bez posunů:
- Podlahová dlažba `koupelna` využívá procedurální mapování `Texture Coordinate: Object` s posunem `Location = (0.20, -0.18, 0.0)` a měřítkem `Scale = (0.85, 0.85, 0.85)`.
- Zdi orientované po ose $X$ ($\pm X$, normála v ose X) využívají materiál `sokl chodba`, který má objektové souřadnice pootočené o $90^\circ$ kolem osy Y.
- Zdi orientované po ose $Y$ ($\pm Y$, normála v ose Y) využívají materiál `sokl chodba.001`, který má objektové souřadnice pootočené o $90^\circ$ kolem osy X.
- Díky tomuto sladění svislé spáry na stěnách a soklech navazují na spáry na podlaze s milimetrovou přesností.

### 4.2 Rozsah soklíků a obkladů podle místností
1. **1.09 Technická místnost**:
   - $15\,\text{cm}$ soklík ($Z \in [0.000, 0.150]\text{ m}$) po celém obvodu všech 4 stěn (včetně jižní stěny $Y = 8.288\text{ m}$ i dveřního ostění).
   - Nad soklíkem ($Z > 0.150\text{ m}$) čistá bílá omítka `Mat_Interior_Wall` / `Mat_Exterior_Wall`.
2. **1.11 Chodba**:
   - $15\,\text{cm}$ soklík po celém obvodu včetně západní, východní, severní i jižní stěny ($Y = 7.100\text{ m}$).
3. **1.01 Zádveří**:
   - $15\,\text{cm}$ soklík po celém obvodu vstupních stěn a ostění.
4. **1.08 WC**:
   - Poloviční obklad do výšky $Z \le 1.150\text{ m}$ na všech čtyřech vnitřních stěnách v materiálu `koupelna` / `sokl chodba.001` v návaznosti na podlahu.
   - Nad kótou $1.150\text{ m}$ čistá bílá omítka.
   - Severní okraj podlahy prodloužen na $Y = 8.1625\text{ m}$ pro zakrytí spáry za toaletou.
5. **1.10 Koupelna**:
   - **Sprchový kout** ($X \in [0.365, 1.368]$, $Y \in [9.900, 10.890]$): plná výška svislých dřevěných lamel (`Plank stena.001`) na západní i jižní stěně v návaznosti na dřevěný podlahový rošt (`Plank 1`).
   - **Ostatní stěny koupelny**: plná výška šedá keramická dlažba navazující na podlahu.
   - **Horní koruna obvodové stěny ($Z = 2.500\text{ m}$)**: vodorovná řezová plocha nese bílou omítku `Mat_Exterior_Wall` (vynechána ze slotu dlažeb).

---

## 5. Základová Deska a Zpevněné Plochy (100% Ortogonální Quad Síť)

### 5.1 Řezy souřadnic
- **Osa $X$**: $[-1.20, 2.19, 5.00, 8.19, 10.00, 11.20]$
- **Osa $Y$**: $[-9.00, -1.20, 0.00, 12.00, 13.20, 18.00]$
- **Výška $Z$**: Horní povrch $Z = 0.000\text{ m}$, spodní hrana $Z = -0.200\text{ m}$ (tloušťka desky $20\text{ cm}$).

### 5.2 Zóny zpevněných ploch
1. **Okapový chodník**: Šířka $1.200\text{ m}$ kolem obvodu celého domu ($X \in [-1.2, 11.2]$, $Y \in [-1.2, 13.2]$).
2. **Přední příjezdová plocha**: Šířka $6.000\text{ m}$, délka $9.000\text{ m}$ ($X \in [2.19, 8.19]$, $Y \in [-9.0, 0.0]$), přesně symetricky vycentrovaná na vchodové dveře.
3. **Zadní terasa**: Šířka $5.000\text{ m}$, hloubka $6.000\text{ m}$ ($X \in [5.00, 10.00]$, $Y \in [12.0, 18.0]$), navazující na francouzské dveře obývacího pokoje.
4. **Materiál dlažby**: `Stone ground tile` / `Mat_Outdoor_Concrete_Paving` (antracitová betonová dlažba).
5. **Reálná výška dlažby & zahradní obrubníky (`Garden_Curbs`)**:
   - Modifikátor `Solidify` na desce ($8\text{ cm}$).
   - Obrubníky tl. $8\text{ cm}$, výška $+3.5\text{ cm}$ nad úroveň dlažby (`Mat_Garden_Curb`).

---

## 6. Světelný Plán (Podle výkresu `svetla 2022.jpg`)

Všechna světla jsou přesně umístěna ve 3D prostoru na výšce stropních bodovek $Z = 2.400\text{ m}$:

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
- **Ortho Scale**: `18.0` (rámuje půdorys domu s chodníky a příjezdovou cestou při výšce stěn 2.5m)
- **Cílový bod (Target)**: $\vec{T} = (5.0, 6.0, 1.25)$
- **Směrový vektor izometrie**: $\vec{D} = \frac{(-1.0, -1.0, \sqrt{2})}{\|\dots\|}$
- **Vzdálenost kamery**: $35.0\text{ m}$

---

## 8. Plná Reprodukovatelnost a Automatizace

Kompletní aplikaci všech obkladů, bisekčních řezů, spárořezů, geometrie podlah a vygenerování kontrolních renderů zajišťuje skript:

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --python apply_all_tiles_and_skirting.py
```
