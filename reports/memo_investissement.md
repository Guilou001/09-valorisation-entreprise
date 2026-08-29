# Mémo de valorisation : Canadien National (CNR.TO), 28 août 2026

Ce mémo n'est ni une recommandation d'achat ni de vente : il établit ce que le cours suppose, le
compare à ce que l'entreprise a livré, et dit à quelles conditions chaque lecture se renverse. Tous
les chiffres portent leur statut ; ils viennent de `results/tables/` du dépôt, régénérables par
`vlab fetch` puis `vlab build`.

## La photographie

Le CN exploite un réseau ferroviaire d'environ 30 000 km (rapporté par la société), dans un
marché nord-américain à très peu d'acteurs, le CP étant l'autre transcontinental canadien.
En quinze exercices (SEC, mesuré) : revenus passés de 9,0 à
17,3 milliards de CAD, marge d'exploitation entre 34 % et 42 %, flux de trésorerie disponible
entre 13 % et 24 % des revenus. Cours au 28 août 2026 : 175,06 $ (rapporté, Yahoo) ; dette nette
20,9 G$ et FCFF moyen 2023-2025 de 4,1 G$ (mesurés, SEC).

## Les trois lectures, et leur tension

1. **Le DCF prudent dit 93 $.** Sous une croissance ancrée sur les revenus réalisés (3,2 % par an
   pendant cinq ans, fondu vers 2 % perpétuel, WACC de 7,8 % aux composants statués), la valeur
   par action ressort à 93 $, soit 47 % sous le cours (modélisé).
2. **Les comparables disent 200 à 225 $.** À la médiane des multiples des trois grands
   ferroviaires américains et du CP (16,6 fois l'EBITDA, 29,8 fois les bénéfices, rapportés de
   Yahoo au 28 août 2026), le CN, qui se paie 14,0 et 22,5 fois, vaudrait 200 $ (EV/EBITDA) à
   225 $ (P/E) : il est le MOINS cher de sa cohorte.
3. **Le DCF inversé fait le pont : le cours suppose 11,9 %.** Pour justifier 175 $, il faut
   11,9 % de croissance annuelle du FCFF pendant cinq ans. Le réalisé est de 7,8 % par an sur 2011-2025, de
   4,0 % seulement sur les dix dernières années (2015-2025), et cette croissance devait beaucoup à l'expansion des marges, qui ne se répète pas à l'infini ;
   les revenus, eux, ont crû de 3,2 % par an.

Certes, la lecture relative (le CN décoté face à ses pairs) et la lecture absolue (le cours
au-dessus du DCF prudent) coexistent sans contradiction : si toute la cohorte ferroviaire embarque
des attentes de croissance élevées, le CN peut être à la fois le moins cher du groupe et au-dessus
de sa valeur intrinsèque prudente. Le juge de paix est la croissance livrée les prochaines années.

## La thèse casse si

| Lecture | Elle casse si | Références chiffrées |
|---|---|---|
| « Le cours est exigeant » (DCF inversé) | le FCFF croît durablement au-dessus de 11,9 % par an, par exemple par un nouveau cycle de marges ou de prix | croissance implicite 11,9 % contre 7,8 % livré sur 2011-2025 (tables `hypotheses.csv`) |
| « Le DCF prudent à 93 $ » | la croissance ancrée sur les revenus (3,2 %) sous-estime le pouvoir de prix ; à 7,8 % (le FCFF réalisé), le modèle donne une valeur nettement plus haute (voir `sensibilite.csv` et le classeur, hypothèses modifiables) | sensibilité : de 56 $ (WACC 9,5 %, g 1 %) à 202 $ (WACC 6 %, g 3 %) |
| « Décoté face aux pairs » | les multiples des pairs se dégonflent (ils embarquent 29,8 fois les bénéfices) plutôt que le CN qui se réévalue | médiane pairs 16,6 × EBITDA contre 14,0 × pour le CN |

## Risques non chiffrés ici

Réglementation (arbitrages Canada-États-Unis, service commun), cycle des matières premières et du
grain, main-d'œuvre et arrêts de travail, climat (feux, inondations sur le réseau), change
CAD-USD. L'exercice 2021 est absent du XBRL de la SEC (déclaré) ; les multiples des pairs sont des
valeurs Yahoo d'un jour donné, pas des consensus lissés.

---

# Investment memo: Canadian National Railway (CNR.TO), August 28, 2026

Not a buy or sell recommendation: this memo states what the price implies, compares it with what
the company has delivered, and spells out what would overturn each reading. Every figure carries
its status (measured from SEC filings, reported from Yahoo on a dated snapshot, or modeled).

CN operates a rail network of roughly 30,000 km (company-reported), in a North American market
with very few players. Over fifteen fiscal years:
revenues up from C$9.0bn to C$17.3bn, operating margins between 34 % and 42 %. At C$175.06, a
prudent DCF (3.2 % growth for five years, the revenue track record, fading to 2 %, WACC 7.8 %)
values the share at C$93; peer-median multiples (16.6 × EBITDA, 29.8 × earnings) imply C$200-225,
CN being the cheapest of its cohort; and the reverse DCF shows the price embeds 11.9 % annual FCFF
growth for five years against 7.8 % delivered over 2011-2025 and 4.0 % over the last ten years. Both readings can hold at once if the
whole rail cohort trades on demanding expectations: the tie-breaker is delivered growth. The
thesis-breaking conditions and the full sensitivity grid are in the tables and in the live-formula
Excel workbook (`reports/classeur_valorisation_cn.xlsx`).
