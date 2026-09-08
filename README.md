# Quelles attentes de croissance se cachent dans le prix d'une action du CN ?

Acheter une action, c'est payer aujourd'hui pour une part de l'argent qu'une entreprise pourra produire demain. La difficulté est de savoir combien elle produira et quel risque on accepte en attendant.

Ce projet prend le Canadien National, une entreprise ferroviaire, et compare trois façons d'estimer sa valeur. Il part aussi du prix observé pour calculer la croissance nécessaire pour le justifier.

L'exercice est daté du **28 août 2026**. Il explique des hypothèses de valorisation et ne donne pas une recommandation d'achat.

## Des prix différents parce que les hypothèses diffèrent

| Lecture | Valeur par action en dollars canadiens |
|---|---:|
| Argent futur ramené à sa valeur actuelle, scénario de base | 93 $ |
| Comparaison avec les résultats des autres ferroviaires | 200 à 225 $ |
| Prix observé le 28 août 2026 | 175,06 $ |

Le scénario de base suppose une croissance initiale de 3,2 % et un coût du capital de 7,8 %. Ce coût représente le rendement demandé par les apporteurs d'argent. [Hypothèses, dates et sources](results/tables/hypotheses.csv).

![Valeurs de l'action selon les hypothèses et les méthodes](results/figures/football_field.png)

Chaque segment montre les valeurs obtenues selon une méthode et ses hypothèses. Le trait du cours indique le prix réellement observé à la date de l'exercice. Le désaccord entre les méthodes rend les hypothèses visibles.

## Retourner le calcul pour comprendre le prix

En gardant les autres hypothèses du modèle, le prix observé exige environ **11,9 % de croissance annuelle** du flux disponible pendant les cinq premières années.

Le flux disponible est l'argent restant pour les prêteurs et les actionnaires après les dépenses nécessaires à l'activité. Sa croissance historique lissée atteint 7,8 % par an entre 2011 et 2025. L'écart indique ce que l'acheteur doit supposer sur l'avenir.

Le [classeur Excel](reports/classeur_valorisation_cn.xlsx) permet de changer les hypothèses et de voir la valeur se recalculer. Un [mémo bilingue](reports/memo_investissement.md) explique les lectures possibles.

## Ce qui limite l'estimation

L'exercice 2021 est absent de la source comptable utilisée et reste vide. Les comparables sont un instantané d'un jour. Une valeur de modèle n'est pas un prix certain, et la croissance déduite du cours dépend des autres paramètres maintenus fixes.

## Refaire les calculs

```bash
uv sync --locked --all-extras
uv run vlab fetch
uv run vlab build
uv run pytest
```

Une nouvelle collecte peut changer le cours et les hypothèses de marché. Les résultats publiés restent ceux de l'instantané daté.

## Pour aller plus loin

[Méthodes, résultats complets et références](docs/ETUDE_DETAILLEE.md) · [Présentation en PDF](rapport/rapport.pdf) · [Citer le projet](CITATION.cff) · [Licence](LICENSE).

## English summary

A dated Canadian National Railway valuation compares cash-flow assumptions, peer multiples and the growth implied by the observed share price. Model values depend on assumptions and are not investment recommendations.
