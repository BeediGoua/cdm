# FIFA Ranking + PDF de calcul FIFA

## Pourquoi le PDF FIFA est important

Nous avons désormais deux choses différentes :

### 1. Les données FIFA Ranking

Issues des endpoints :

```text
https://api.fifa.com/api/v3/rankings/?gender=1&count=211
https://api.fifa.com/api/v3/rankings/byCountry/<CODE>?gender=1
https://api.fifa.com/api/v3/rankings/byCountry/<CODE>/aggregated?gender=1
```

Elles donnent :

- rang FIFA
- points FIFA
- historique FIFA
- variation de rang
- variation de points
- confédération

---

### 2. Le PDF FIFA

Le PDF explique :

```text
comment FIFA calcule ces points
```

Autrement dit :

```text
API FIFA = résultat du calcul
PDF FIFA = mécanisme du calcul
```

Les deux sont complémentaires.

---

## Ce qu’il ne faut pas faire

Il ne faut pas remplacer :

```text
Elo
Poisson
Monte Carlo
```

par :

```text
formule FIFA
```

Pourquoi ?

```text
Classement FIFA = classement des équipes
Modèle Poisson = prédiction des matchs
Monte Carlo = simulation du tournoi
```

Ils n’ont pas le même rôle.

---

# Nouvelle hiérarchie des modèles

## MVP

Force équipe :

```text
strength(team) = elo(team)
```

Utilisation :

```text
teamStrength.ts
```

Le classement FIFA est seulement affiché dans le dashboard.

## V1.5

Ajout FIFA Ranking API.

```text
strength(team)
= 0.8 × Elo + 0.2 × FIFA Points
```

ou

```text
strength(team)
= 0.7 × Elo + 0.3 × FIFA Points
```

Fichier :

```text
src/domain/prediction/teamStrength.ts
```

## V2

Ajout historique FIFA.

Nouvelles variables :

- rankingTrend3Months
- rankingTrend1Year
- pointsTrend1Year
- rankVolatility
- pointsVolatility

Calculées à partir de :

```text
api/v3/rankings/byCountry
```

Fichier :

```text
src/domain/prediction/fifaTrendFeatures.ts
```

## V3

Ajout mise à jour dynamique FIFA.

On utilise alors le PDF officiel.

---

# Intégration du PDF FIFA

## Nouveau fichier

```text
src/domain/live/updateFifaRatingAfterResult.ts
```

Responsabilité :

```text
mettre à jour les points FIFA après un match réel
```

Le PDF donne :

```text
Pnew = Pbefore + I × (W - We)
```

avec :

- Pbefore = points FIFA actuels
- I = importance du match
- W = résultat réel
- We = résultat attendu

## Exemple

Avant match :

```text
France : 1877 points
Brésil : 1845 points
```

Résultat :

```text
France 2-0 Brésil
```

Alors :

```text
France : 1877 → 1884
Brésil : 1845 → 1838
```

Ces nouveaux points deviennent :

```text
updatedFifaPoints
```

---

# Impact sur le Live Update

Avant tournoi :

```text
Elo fixe
FIFA fixe
```

Pendant tournoi :

```text
match réel
↓
mise à jour Elo
↓
mise à jour FIFA
↓
nouveau teamStrength
↓
nouveau Monte Carlo
```

Le système devient adaptatif sans avoir besoin de réentraîner un modèle.

---

# Nouveau flux Live

```text
score réel
↓
applyRealResult.ts
↓
updateEloAfterResult.ts
↓
updateFifaRatingAfterResult.ts
↓
teamStrength.ts
↓
simulateTournament.ts
↓
runMonteCarlo.ts
```

---

# Impact sur le Dashboard

Nouveau bloc :

```text
FIFA Rating Evolution
```

Fichier :

```text
src/features/dashboard/FifaRankingEvolution.tsx
```

Affichage :

```text
France
Rank : 3 → 1
Points : 1870 → 1877
Variation : +7
```

---

# Cartographie mise à jour des endpoints FIFA

## Endpoint principal

```text
https://api.fifa.com/api/v3/rankings/?gender=1&count=211
```

Usage :

- teams.json
- fifa_rankings_current.json
- fifaRankingService.ts
- teamStrength.ts
- dashboard

Données :

- Rank
- PrevRank
- Points
- PrevPoints
- Confederation
- Matches

## Historique pays

```text
https://api.fifa.com/api/v3/rankings/byCountry/FRA?gender=1
```

Usage :

- fifaTrendFeatures.ts
- RankingTrendChart.tsx

Données :

- historique rang
- historique points
- historique matchs

Permet :

- rankingTrend1Year
- pointsTrend1Year
- volatilité

## Statistiques agrégées

```text
https://api.fifa.com/api/v3/rankings/byCountry/FRA/aggregated?gender=1
```

Usage :

- TeamProfileCard.tsx

Données :

- AverageRank
- BestRankingYear
- WorstRankingYear

Exemple :

```text
France
rang actuel : 1
rang moyen historique : 7.86
```

## Snapshots historiques

```text
https://inside.fifa.com/api/ranking-overview?locale=fr&dateId=id14870
```

Usage :

- fifa_rankings_snapshot_id14870.json
- backtest
- historique global

Permet :

```text
reconstituer le classement à une date donnée
```

## Drapeaux

```text
https://api.fifa.com/api/v3/picture/flags-sq-2/FRA
```

Usage :

- Flag.tsx
- TeamBadge.tsx

## Confédérations

```text
https://api.fifa.com/api/v3/picture/confederations-sq-2/UEFA
```

Usage :

- Dashboard
- Filtres
- Profils équipes

---

# Nouveaux fichiers à ajouter

## Domain

```text
src/domain/prediction/fifaTrendFeatures.ts
src/domain/prediction/fifaStrength.ts
src/domain/live/updateFifaRatingAfterResult.ts
```

## Services

```text
src/services/fifaRankingService.ts
src/services/fifaCountryRankingService.ts
src/services/fifaRankingSnapshotService.ts
src/services/fifaFlagService.ts
```

## Dashboard

```text
src/features/dashboard/FifaRankingTable.tsx
src/features/dashboard/FifaRankingEvolution.tsx
src/features/dashboard/RankingTrendChart.tsx
src/features/dashboard/TeamProfileCard.tsx
```

---

# Priorités réelles du projet

## Priorité 1

- règles FIFA
- groupes
- calendrier
- bracket

## Priorité 2

- Elo
- Poisson
- Monte Carlo

## Priorité 3

- API FIFA Ranking
- points FIFA
- drapeaux
- confédérations

## Priorité 4

- historique FIFA
- features temporelles FIFA
- comparaison FIFA vs Elo

## Priorité 5

- PDF FIFA
- mise à jour dynamique FIFA
- updateFifaRatingAfterResult.ts

## Priorité 6

- fusion Elo + FIFA
- force hybride
- adaptation pendant le tournoi

---

# Synthèse finale

Nous avons maintenant deux systèmes complémentaires.

## Système 1

```text
Elo + Poisson + Monte Carlo
```

Objectif :

```text
prédire et simuler
```

## Système 2

```text
API FIFA + PDF FIFA
```

Objectif :

```text
mesurer la force réelle et la faire évoluer
```

## Projet final

```text
Données FIFA officielles
+
Classement FIFA
+
Historique FIFA
+
PDF officiel de calcul FIFA
+
Elo
+
Poisson
+
Monte Carlo
+
Live Update
```

Ce qui permet d’avoir un simulateur qui fonctionne avant la Coupe du Monde, mais aussi pendant la compétition en recalculant automatiquement les probabilités à partir des résultats réels et de l’évolution des forces des équipes.
