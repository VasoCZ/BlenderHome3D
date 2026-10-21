# Pravidla projektu: 3D model rodinného domu (Home Assistant Floorplan)

## 1. Režim práce a kontrola chyb
- **Důkladná sebekontrola a preciznost**: Po každé úpravě vždy pečlivě a důsledně ověř stav modelu, materiálů a hierarchie objektů. Předcházej chybám kontrolou výstupů.
- **Zákaz promptů /learn**: V rámci tohoto projektu už nikdy nenabízej ani nevypisuj žádné návrhy na příkaz `/learn`.

## 2. Standard okenních žaluzií
- **Materiál a provedení**: Všechna obytná okna (1.03 Kuchyně, 1.04 Obývací pokoj, 1.05 Ložnice jih, 1.06 Pokoj jihozápad, 1.07 Pracovna západ) mají jednotné černé horizontální žaluzie v materiálu `Mat_Kitchen_Black_Metal`.
- **Komponenty žaluzie**: Každá sestava žaluzií obsahuje horní krycí kazetu, horizontální lamely (rozteč 50–55 mm, náklon 25°–30°), spodní zatěžovací lištu a boční vodící lanka.
- **Francouzské / terasové dveře**: U dvoukřídlých dveří na terasu (1.04) se žaluzie člení na dvě samostatná křídla (pro každé dveřní křídlo zvlášť) s délkou od podlahového prahu ($Z \approx 0.12$ m) až po horní rám ($Z \approx 2.18$ m).

## 3. Integrita modelu pro Home Assistant
- **Fyzický realismus bez falešných efektů**: Pro HA floorplan nemodeluj žádné falešné 2D/3D plameny v krbu, umělé záře sporáků ani svítící plochy spotřebičů v klidovém stavu.
- **Průchodnost a kolmost**: Prvky u šikmých zdí orientuj striktně kolmo k rovině zdi. Nábytek nesmí zasahovat do dráhy otevírání dveří (např. jídelní stůl musí zůstat před pomyslnou kolmicí dveří na terasu).

## 4. Zákaz 'Minecraft' textur a zjednodušených bloků
- **Žádné procedurální cihlové mřížky ani schematické bloky**: Při tvorbě či úpravách nových prvků zásadně nepoužívej zjednodušené hranoly s procedurálními mřížkami připomínajícími Minecraft.
- **Vysoká vizuální kvalita a detailní modelování**: Každý nově přidaný kus nábytku a vybavení musí být plnohodnotný, realistický model s autentickými PBR texturami a reálnými proporcemi podle fotografií.

## 5. Standard dřevodekoru (Kronospan K003 Gold Craft Oak)
- **Jednotný dubový dekor**: Jídelní stůl, dřevěné prvky v obývacím pokoji (TV konzole, konferenční stolek, prosklená vitrína, zrcadlová police), komoda v ložnici (1.05) i Kallax v dětském pokoji (1.06) mají jednotný reálný dekor `Mat_Kronospan_K003_Gold_Craft_Oak`.
