#set document(title: "Quelles attentes de croissance se cachent dans le prix d'une action du CN ?", author: "Guillaume Vaudescal")
#set page(
  paper: "a4",
  margin: (x: 2.2cm, y: 2.4cm),
  numbering: "1 / 1",
  footer: context [
    #set text(size: 8pt, fill: luma(90))
    #grid(columns: (1fr, auto), align: (left, right),
      [valuation-lab-ca], [#counter(page).display("1 / 1", both: true)])
  ],
)
#set text(font: ("Helvetica", "Arial", "DejaVu Sans"), size: 10pt, lang: "fr")
#set par(justify: true, leading: 0.68em, spacing: 1.1em)
#set heading(numbering: none)
#show heading.where(level: 2): it => block(above: 1.6em, below: 0.8em, text(size: 13pt, it))
#show heading.where(level: 3): it => block(above: 1.2em, below: 0.6em, text(size: 11pt, it))
#show raw.where(block: true): it => block(
  fill: luma(246), inset: 8pt, radius: 3pt, width: 100%, text(size: 8.5pt, it))
#show raw.where(block: false): it => text(size: 9pt, fill: rgb("#1a3f66"), it)
#show quote.where(block: true): it => block(
  inset: (left: 10pt), stroke: (left: 1.5pt + luma(180)),
  text(style: "italic", fill: luma(45), it.body))
// la table NE DOIT PAS être enfermée dans un par() : Typst 0.15 la supprime alors
// entièrement, sans erreur. Le réglage se pose donc dans la portée du bloc.
#show table: it => block(above: 1.1em, below: 1.1em,
  [#set par(justify: false); #text(size: 8.8pt, it)])
#show figure: it => block(above: 1.4em, below: 1.4em, it)
#show figure.caption: it => text(size: 8.5pt, fill: luma(70), it)
#show link: it => text(fill: rgb("#0072B2"), it)

#align(center)[
  #block(width: 100%)[
    #text(size: 18pt, weight: "bold")[Quelles attentes de croissance se cachent dans le prix d'une action du CN ?]
    #v(0.6em)
    #text(size: 10pt, fill: luma(70))[Guillaume Vaudescal · 2026-09-08 · #link("https://github.com/Guilou001/09-valorisation-entreprise")[Guilou001/09-valorisation-entreprise]]
  ]
]
#v(1.2em)
#line(length: 100%, stroke: 0.6pt + luma(190))
#v(0.8em)

Acheter une action, c'est payer aujourd'hui pour une part de l'argent qu'une entreprise pourra produire demain. La difficulté est de savoir combien elle produira et quel risque on accepte en attendant.

Ce projet prend le Canadien National, une entreprise ferroviaire, et compare trois façons d'estimer sa valeur. Il part aussi du prix observé pour calculer la croissance nécessaire pour le justifier.

L'exercice est daté du *28 août 2026*. Il explique des hypothèses de valorisation et ne donne pas une recommandation d'achat.

== Des prix différents parce que les hypothèses diffèrent

#table(
  columns: 2,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: left + top,
  inset: 5pt,
    [*Lecture*],
    [*Valeur par action en dollars canadiens*],
    [Argent futur ramené à sa valeur actuelle, scénario de base],
    [93 \$],
    [Comparaison avec les résultats des autres ferroviaires],
    [200 à 225 \$],
    [Prix observé le 28 août 2026],
    [175,06 \$],
)

Le scénario de base suppose une croissance initiale de 3,2 % et un coût du capital de 7,8 %. Ce coût représente le rendement demandé par les apporteurs d'argent. #link("results/tables/hypotheses.csv")[Hypothèses, dates et sources].

#figure(image("../results/figures/football_field.png", width: 100%), caption: [Valeurs de l'action selon les hypothèses et les méthodes])

Chaque segment montre les valeurs obtenues selon une méthode et ses hypothèses. Le trait du cours indique le prix réellement observé à la date de l'exercice. Le désaccord entre les méthodes rend les hypothèses visibles.

== Retourner le calcul pour comprendre le prix

En gardant les autres hypothèses du modèle, le prix observé exige environ *11,9 % de croissance annuelle* du flux disponible pendant les cinq premières années.

Le flux disponible est l'argent restant pour les prêteurs et les actionnaires après les dépenses nécessaires à l'activité. Sa croissance historique lissée atteint 7,8 % par an entre 2011 et 2025. L'écart indique ce que l'acheteur doit supposer sur l'avenir.

Le #link("reports/classeur_valorisation_cn.xlsx")[classeur Excel] permet de changer les hypothèses et de voir la valeur se recalculer. Un #link("reports/memo_investissement.md")[mémo bilingue] explique les lectures possibles.

== Ce qui limite l'estimation

L'exercice 2021 est absent de la source comptable utilisée et reste vide. Les comparables sont un instantané d'un jour. Une valeur de modèle n'est pas un prix certain, et la croissance déduite du cours dépend des autres paramètres maintenus fixes.

== Refaire les calculs

#raw("uv sync --locked --all-extras\nuv run vlab fetch\nuv run vlab build\nuv run pytest", block: true, lang: "bash")

Une nouvelle collecte peut changer le cours et les hypothèses de marché. Les résultats publiés restent ceux de l'instantané daté.

== Pour aller plus loin

#link("docs/ETUDE_DETAILLEE.md")[Méthodes, résultats complets et références] · #link("rapport/rapport.pdf")[Présentation en PDF] · #link("CITATION.cff")[Citer le projet] · #link("LICENSE")[Licence].

== English summary

A dated Canadian National Railway valuation compares cash-flow assumptions, peer multiples and the growth implied by the observed share price. Model values depend on assumptions and are not investment recommendations.
