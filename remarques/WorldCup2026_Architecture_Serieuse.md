# World Cup 2026 Intelligence Simulator - Architecture Sérieuse

## Vision du projet

Un simulateur probabiliste de Coupe du Monde 2026 combinant :

- règles officielles FIFA
- moteur de bracket
- prédiction de scores par modèle Elo-Poisson
- simulation Monte Carlo

Le projet doit rester sérieux, cohérent et réalisable.

---

# Sources principales

## FIFA

Utilisation :

- format officiel du tournoi
- groupes
- calendrier
- stades
- règles de qualification
- règles de départage

Format officiel :

- 48 équipes
- 12 groupes
- 2 premiers qualifiés
- 8 meilleurs troisièmes
- phase finale à 32 équipes

## Elo Ratings

Sources :

- World Football Elo Ratings
- International Football Elo Ratings

Utilisation :

- force des équipes
- modèle probabiliste

## Historique des matchs

Sources :

- Kaggle International Football Results
- GitHub martj42/international_results

Utilisation :

- backtesting
- calibration
- création des features

---

# Architecture réajustée

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
    predictor/
    bracket/
    dashboard/

  components/
    ui/
    football/

  store/
  services/
  tests/
```

À ne pas créer immédiatement :

```text
monitoring/
supabase/
charts/
venue-map/
advanced-models/
```

---

# Données

## src/data/raw/

Données proches de leur source.

```text
src/data/raw/fifa_groups.json
src/data/raw/fifa_schedule.json
src/data/raw/fifa_venues.json
src/data/raw/elo_ratings.json
src/data/raw/historical_results.csv
```

Sources :

- FIFA
- Elo Ratings
- Kaggle
- GitHub

Les PDF servent uniquement à comprendre la logique du site.

---

## src/data/normalized/teams.json

Exemple :

```json
[
  {
    "id": "fra",
    "nameFr": "France",
    "nameEn": "France",
    "flagCode": "fr",
    "confederation": "UEFA",
    "elo": 2062,
    "fifaRank": 3
  }
]
```

Source :

- FIFA
- Elo Ratings
- FIFA Ranking

---

## src/data/normalized/groups.json

```json
{
  "A": ["mex", "rsa", "kor", "playoff_uefa_d"],
  "B": ["can", "playoff_uefa_a", "qat", "sui"]
}
```

Source :

- FIFA Final Draw

---

## src/data/normalized/groupMatches.json

```json
[
  {
    "id": "M001",
    "group": "A",
    "homeTeamId": "mex",
    "awayTeamId": "rsa",
    "date": "2026-06-11",
    "timeLocal": "14:00",
    "venueId": "azteca"
  }
]
```

Source :

- FIFA Match Schedule

---

## src/data/normalized/bracketRules.json

Fichier critique.

```json
{
  "roundOf32": [
    {
      "id": "R32_1",
      "homeSlot": "1A",
      "awaySlot": "2C"
    }
  ]
}
```

Source :

- FIFA
- vérification avec les PDF

---

# Moteur tournoi

## computeGroupStandings.ts

Objectif :

- calculer les classements

Formules :

```text
points = 3 × victoires + 1 × nuls
goalDifference = goalsFor - goalsAgainst
```

Type :

```ts
type Standing = {
  teamId: string
  played: number
  wins: number
  draws: number
  losses: number
  goalsFor: number
  goalsAgainst: number
  goalDifference: number
  points: number
}
```

---

## tiebreakers.ts

MVP :

```text
points
différence de buts
buts marqués
fair-play
choix manuel
```

Version avancée :

```text
confrontations directes
différence de buts confrontation
buts marqués confrontation
fair-play
tirage au sort
```

---

## rankThirdPlacedTeams.ts

Objectif :

- sélectionner les 8 meilleurs troisièmes

Critères :

```text
points
différence de buts
buts marqués
fair-play
```

---

## buildBracket.ts

Objectif :

- construire le tableau final

---

## propagateWinner.ts

Objectif :

- envoyer le vainqueur au tour suivant
- nettoyer les tours dépendants

---

# Modèle probabiliste

## Philosophie

Pas de Dixon-Coles dans le MVP.

MVP :

```text
Elo + Poisson
```

---

## teamStrength.ts

Objectif :

```text
strength(team) = elo(team)
```

---

## expectedGoals.ts

Objectif :

Calcul des buts attendus.

Formules :

```text
diff = eloA - eloB

lambdaA = baseGoals × exp(diff / scale)
lambdaB = baseGoals × exp(-diff / scale)
```

Paramètres MVP :

```text
baseGoals = 1.35
scale = 800
```

Interprétation :

- équipe forte → lambda augmente
- équipe faible → lambda diminue

---

## scoreDistribution.ts

Objectif :

Calculer :

```text
P(scoreA = x, scoreB = y)
```

Poisson :

```text
P(X = k) = exp(-lambda) × lambda^k / k!
```

Score exact :

```text
P(A=x,B=y)
= Poisson(x;lambdaA)
× Poisson(y;lambdaB)
```

Hypothèse :

- indépendance des buts

Limite :

- petits scores parfois mal calibrés

---

## predictMatch.ts

Objectif :

Calculer :

```text
P(victoire)
P(nul)
P(défaite)
```

Agrégation :

```text
P(A gagne) = somme x > y
P(nul) = somme x = y
P(B gagne) = somme x < y
```

---

# Simulation Monte Carlo

## simulateMatch.ts

Objectif :

- tirer un score aléatoire

---

## simulateTournament.ts

Étapes :

1. simuler groupes
2. calculer classements
3. sélectionner meilleurs troisièmes
4. construire bracket
5. simuler phase finale
6. retourner champion

---

## runMonteCarlo.ts

Objectif :

- répéter N tournois

Formule :

```text
P(champion équipe i)
= titres_i / N
```

Erreur :

```text
erreur ≈ 1 / sqrt(N)
```

Recommandation MVP :

```text
10 000 simulations
```

---

# Évaluation

## backtest.ts

Principe :

```text
train : avant 2022
test : Coupe du Monde 2022
```

---

## logLoss.ts

```text
LogLoss
= - moyenne(log(probabilité du résultat réel))
```

Plus petit = meilleur.

---

## calibration.ts

Objectif :

Vérifier :

```text
70 % prédit
≈
70 % observé
```

---

# Interface MVP

## Page 1 - Setup

- choisir barragistes
- voir groupes
- voir calendrier

## Page 2 - Predictions

- auto-remplissage Elo
- saisie manuelle
- classement automatique

## Page 3 - Bracket

- tableau final
- choix des vainqueurs
- champion

## Page 4 - Dashboard

- probabilité qualification
- probabilité demi-finale
- probabilité finale
- probabilité champion

---

# Structure finale

```text
src/
  data/
    raw/
      fifa_groups.json
      fifa_schedule.json
      fifa_venues.json
      elo_ratings.json
      historical_results.csv

    normalized/
      teams.json
      groups.json
      playoffs.json
      groupMatches.json
      venues.json
      bracketRules.json

  domain/
    tournament/
      computeGroupStandings.ts
      tiebreakers.ts
      rankThirdPlacedTeams.ts
      buildSlotMap.ts
      buildBracket.ts
      propagateWinner.ts
      tournament.types.ts

    prediction/
      teamStrength.ts
      expectedGoals.ts
      poisson.ts
      scoreDistribution.ts
      predictMatch.ts
      prediction.types.ts

    simulation/
      simulateMatch.ts
      simulateTournament.ts
      runMonteCarlo.ts
      aggregateResults.ts
      simulation.types.ts

    evaluation/
      backtest.ts
      logLoss.ts
      calibration.ts

  features/
    setup/
      PlayoffSelector.tsx
      GroupOverview.tsx
      SchedulePreview.tsx

    predictions/
      MatchPredictionTable.tsx
      ScoreInput.tsx
      StandingsPreview.tsx

    bracket/
      BracketView.tsx
      KnockoutMatchCard.tsx
      ChampionSummary.tsx

    dashboard/
      ProbabilityTable.tsx
      ChampionRanking.tsx

  components/
    ui/
      Button.tsx
      Card.tsx
      Modal.tsx

    football/
      TeamBadge.tsx
      Flag.tsx
      MatchCard.tsx

  services/
    dataLoader.ts
    storageService.ts
    eloService.ts

  tests/
    tournament/
    prediction/
    simulation/
```

---

# Roadmap

## MVP

```text
Règles FIFA
+ Bracket
+ Elo
+ Poisson
+ Monte Carlo
+ Dashboard simple
```

## V2

```text
Backtest
Calibration
Scénarios
```

## V3

```text
Dixon-Coles
xG
Fatigue
Monitoring
```

---

# Conclusion

Le projet doit démontrer :

- modélisation probabiliste
- simulation Monte Carlo
- ingénierie logicielle
- manipulation de données
- évaluation de modèle
- visualisation de probabilités

Sans tomber dans une architecture trop complexe ou impossible à terminer.
