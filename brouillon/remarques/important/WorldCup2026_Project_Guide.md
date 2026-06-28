# World Cup 2026 Intelligence Simulator

## Objectif

Développer une application web permettant de simuler la Coupe du Monde 2026 à partir :

- des règles officielles FIFA
- d'un modèle Elo-Poisson pour les scores
- d'une simulation Monte Carlo
- d'un dashboard de probabilités

---

# Sources de données

## FIFA - Groupes officiels

Lien :
https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/final-draw-results

Utilisation :
- groups.json
- vérification des équipes qualifiées
- structure officielle des groupes

## FIFA - Calendrier et stades

Lien :
https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/match-schedule-fixtures-results-teams-stadiums

Utilisation :
- groupMatches.json
- venues.json
- calendrier complet

## FIFA - Règles et départages

Lien :
https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/groups-how-teams-qualify-tie-breakers

Utilisation :
- tiebreakers.ts
- rankThirdPlacedTeams.ts

## FIFA - Scores et résultats

Lien :
https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/scores-fixtures

Utilisation :
- mise à jour des résultats réels
- service d'import futur

## World Football Elo Ratings

Lien :
https://eloratings.net/

Utilisation :
- force des équipes
- teamStrength.ts
- expectedGoals.ts

## FIFA Ranking

Lien :
https://inside.fifa.com/fifa-world-ranking/men

Utilisation :
- variable secondaire
- comparaison avec Elo

## Historique des matchs internationaux

Kaggle :
https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017

GitHub :
https://github.com/martj42/international_results

Utilisation :
- backtesting
- calibration
- création de features

## Dixon-Coles

Article :
https://rss.onlinelibrary.wiley.com/doi/abs/10.1111/1467-9876.00065

Tutoriel :
https://dashee87.github.io/football/python/predicting-football-results-with-statistical-modelling-dixon-coles-and-time-weighting/

Utilisation :
- version avancée du modèle

---

# Mathématiques utilisées

## 1. Classement des groupes

points = 3 × victoires + 1 × nuls

goalDifference = goalsFor - goalsAgainst

Utilisé dans :

- computeGroupStandings.ts

---

## 2. Elo

Probabilité attendue :

E_A = 1 / (1 + 10^(-(R_A - R_B)/400))

Utilisé dans :

- teamStrength.ts

---

## 3. Buts attendus

diff = Elo_A - Elo_B

lambda_A = baseGoals × exp(diff / scale)

lambda_B = baseGoals × exp(-diff / scale)

Valeurs MVP :

- baseGoals = 1.35
- scale = 800

Utilisé dans :

- expectedGoals.ts

---

## 4. Loi de Poisson

P(X = k) = exp(-lambda) × lambda^k / k!

Utilisé dans :

- poisson.ts
- scoreDistribution.ts

---

## 5. Probabilités victoire / nul / défaite

P(A gagne) = somme des scores où x > y

P(nul) = somme des scores où x = y

P(B gagne) = somme des scores où x < y

Utilisé dans :

- predictMatch.ts

---

## 6. Monte Carlo

P(champion) = nombre de titres / nombre de simulations

Exemple :

1180 titres sur 10000 simulations

=> 11.8 %

Erreur approximative :

erreur ≈ 1 / sqrt(N)

Utilisé dans :

- runMonteCarlo.ts

---

## 7. Log Loss

LogLoss = - moyenne(log(probabilité du résultat réel))

Utilisé dans :

- logLoss.ts

---

# Architecture MVP

```text
src/
  data/
    raw/
    normalized/

  domain/
    tournament/
    prediction/
    simulation/
    evaluation/

  features/
    setup/
    predictions/
    bracket/
    dashboard/
```

---

# Ordre de développement

## Phase 1

Données FIFA

- teams.json
- groups.json
- groupMatches.json
- venues.json
- bracketRules.json

## Phase 2

Moteur tournoi

- computeGroupStandings.ts
- tiebreakers.ts
- rankThirdPlacedTeams.ts
- buildBracket.ts
- propagateWinner.ts

## Phase 3

Modèle probabiliste

- teamStrength.ts
- expectedGoals.ts
- poisson.ts
- scoreDistribution.ts
- predictMatch.ts

## Phase 4

Monte Carlo

- simulateMatch.ts
- simulateTournament.ts
- runMonteCarlo.ts

## Phase 5

Évaluation

- backtest.ts
- logLoss.ts
- calibration.ts

---

# Version finale visée

Règles FIFA
+ Elo
+ Poisson
+ Monte Carlo
+ Dashboard probabiliste

Sorties :

- probabilité de qualification
- probabilité d'atteindre les quarts
- probabilité d'atteindre les demi-finales
- probabilité d'atteindre la finale
- probabilité d'être champion
