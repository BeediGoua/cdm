# World Cup 2026 — Plan projet, modèles et prochaines étapes

## 1. Objectif du projet

Construire un simulateur probabiliste de Coupe du Monde 2026 capable de :

- charger et normaliser les données officielles du tournoi ;
- intégrer les ratings Elo des équipes ;
- enrichir les équipes avec les données FIFA Ranking ;
- produire des prédictions de scores avec un modèle Elo-Poisson ;
- simuler le tournoi complet avec Monte Carlo ;
- intégrer les résultats réels pendant la compétition ;
- recalculer les classements, les forces des équipes et les probabilités après chaque journée ;
- comparer plusieurs versions de modèle pour vérifier si chaque amélioration apporte réellement de la valeur.

L’objectif n’est pas seulement de faire un simulateur visuel.

L’objectif est de construire un vrai projet data science :

```text
données fiables
↓
normalisation propre
↓
modèle probabiliste simple
↓
simulation Monte Carlo
↓
évaluation
↓
améliorations mesurées
```

Le simulateur doit fonctionner dans trois situations :

```text
avant tournoi
→ aucune donnée réelle, simulation complète

pendant tournoi
→ scores réels renseignés, matchs joués figés, simulation des matchs restants

après tournoi
→ comparaison entre prédictions et résultats réels
```

---

## 2. Vision globale du projet

Le projet repose sur cinq blocs principaux :

```text
1. Données tournoi
2. Données équipes
3. Modèle de score
4. Simulation tournoi
5. Live update
```

### 2.1 Données tournoi

Elles décrivent la structure officielle de la Coupe du Monde 2026 :

- groupes ;
- équipes ;
- calendrier ;
- stades ;
- phase finale ;
- règles des meilleurs troisièmes ;
- règles de classement.

Fichiers concernés :

```text
src/data/normalized/groups.json
src/data/normalized/groupMatches.json
src/data/normalized/venues.json
src/data/normalized/bracketRules.json
src/data/normalized/playoffs.json
```

---

### 2.2 Données équipes

Elles décrivent chaque équipe :

- identifiant interne ;
- code FIFA ;
- nom ;
- groupe ;
- confédération ;
- drapeau ;
- Elo ;
- rang FIFA ;
- points FIFA ;
- source de l’Elo ;
- niveau de confiance.

Fichier central :

```text
src/data/normalized/teams.json
```

Ce fichier est très important parce qu’il alimente directement :

```text
TeamBadge
GroupOverview
poisson_model.py
simulate_match.py
run_monte_carlo.py
ProbabilityTable
```

Exemple attendu :

```json
{
  "id": "fra",
  "fifaCode": "FRA",
  "nameFr": "France",
  "nameEn": "France",
  "group": "I",
  "confederation": "UEFA",
  "fifaRank": 1,
  "fifaPoints": 1877.32,
  "elo": 2062,
  "eloRank": 3,
  "eloSource": "manual",
  "eloDate": "2026-06-09",
  "sourceConfidence": "medium",
  "flagUrl": "https://api.fifa.com/api/v3/picture/flags-sq-2/FRA"
}
```

---

### 2.3 Modèle de score

Le modèle de score transforme une différence de force entre deux équipes en probabilités de score.

Dans la V1 :

```text
Elo
↓
différence Elo
↓
λ_A et λ_B
↓
Poisson
↓
probabilités de score
```

Le modèle reste volontairement simple au départ.

---

### 2.4 Simulation tournoi

La simulation utilise les probabilités de score pour jouer le tournoi des milliers de fois.

Elle produit :

- probabilité de sortir des groupes ;
- probabilité d’atteindre les 8es ;
- probabilité d’atteindre les quarts ;
- probabilité d’atteindre les demies ;
- probabilité d’atteindre la finale ;
- probabilité d’être champion.

---

### 2.5 Live update

Le live update permet d’utiliser le simulateur pendant la Coupe du Monde.

Après chaque journée :

```text
scores réels
↓
matchs joués figés
↓
classements recalculés
↓
Elo éventuellement mis à jour
↓
points FIFA éventuellement mis à jour
↓
Monte Carlo relancé sur les matchs restants
```

Fichier central :

```text
src/data/raw/real_results.json
```

---

## 3. Sources de données

### 3.1 Sources principales

### FIFA

Rôle :

```text
source officielle du tournoi
```

Utilisation :

- format officiel ;
- groupes ;
- calendrier ;
- stades ;
- règles de qualification ;
- règles de départage ;
- rang FIFA ;
- points FIFA ;
- drapeaux ;
- confédérations.

Fichiers concernés :

```text
src/data/raw/fifa_rankings_current.json
src/data/normalized/fifa_rankings_current.json
src/data/normalized/teams.json
```

Endpoint FIFA Ranking validé :

```text
https://api.fifa.com/api/v3/rankings/?gender=1&count=211
```

---

### OpenFootball 2026

Rôle :

```text
source ouverte utile pour calendrier, stades, bracket et fichiers texte structurés
```

Fichiers utiles :

```text
openfootball_cup.txt
openfootball_cup_finals.txt
openfootball_stadiums.csv
openfootball_quali_playoffs.txt
```

Utilisation :

```text
groupMatches.json
venues.json
bracketRules.json
playoffs.json
```

Attention :

OpenFootball est très utile, mais FIFA reste la source officielle.

---

### FootballRatings / World Football Elo

Rôle :

```text
source Elo
```

Utilisation :

```text
src/data/raw/footballratings_elo.csv
src/data/raw/elo_ratings_manual.json
src/data/normalized/teams.json
```

Décision actuelle :

```text
Pour la V1, on accepte un fichier Elo manuel complet.
La formule Elo servira ensuite à mettre à jour les ratings après les matchs.
```

Important :

```text
Elo initial = valeur de départ
formule Elo = mise à jour après résultat
```

---

### martj42 international_results

Rôle :

```text
historique pour calibration, backtesting et évaluation
```

Fichiers :

```text
historical_results.csv
shootouts.csv
goalscorers.csv
```

Dans le projet :

```text
src/data/raw/historical_results.csv
src/data/processed/matches_clean.csv
```

Utilisation :

- calcul de `baseGoals` ;
- calibration de `scale` ;
- backtest ;
- Log Loss ;
- Brier Score ;
- Calibration Curve ;
- Reliability Diagram.

---

## 4. Fichiers attendus

### 4.1 Données brutes

```text
src/data/raw/
  fifa_rankings_current.json
  footballratings_elo.csv
  elo_ratings_manual.json
  openfootball_cup.txt
  openfootball_cup_finals.txt
  openfootball_stadiums.csv
  openfootball_quali_playoffs.txt
  historical_results.csv
  shootouts.csv
  goalscorers.csv
  real_results.json
```

---

### 4.2 Données normalisées

```text
src/data/normalized/
  teams.json
  groups.json
  groupMatches.json
  venues.json
  bracketRules.json
  playoffs.json
  fifa_rankings_current.json
```

---

### 4.3 Données traitées

```text
src/data/processed/
  matches_clean.csv
```

---

## 5. Structure des fichiers clés

### 5.1 teams.json

Rôle :

```text
fichier central des équipes
```

Doit contenir :

- `id`
- `fifaCode`
- `nameFr`
- `nameEn`
- `group`
- `confederation`
- `fifaRank`
- `fifaPoints`
- `elo`
- `eloRank`
- `eloSource`
- `eloDate`
- `sourceConfidence`
- `flagUrl`

Exemple :

```json
{
  "id": "fra",
  "fifaCode": "FRA",
  "nameFr": "France",
  "nameEn": "France",
  "group": "I",
  "confederation": "UEFA",
  "fifaRank": 1,
  "fifaPoints": 1877.32,
  "elo": 2062,
  "eloRank": 3,
  "eloSource": "manual",
  "eloDate": "2026-06-09",
  "sourceConfidence": "medium",
  "flagUrl": "https://api.fifa.com/api/v3/picture/flags-sq-2/FRA"
}
```

---

### 5.2 groups.json

Rôle :

```text
composition des groupes
```

Exemple :

```json
{
  "A": ["mex", "rsa", "kor", "cze"],
  "B": ["can", "bih", "qat", "sui"],
  "I": ["fra", "sen", "irq", "nor"]
}
```

À vérifier :

- tous les IDs doivent exister dans `teams.json` ;
- aucun alias non résolu ne doit rester ;
- les placeholders de barrages doivent être clairement identifiés.

---

### 5.3 groupMatches.json

Rôle :

```text
calendrier des matchs de groupe
```

Doit contenir :

- `id`
- `group`
- `homeTeamId`
- `awayTeamId`
- `date`
- `timeLocal`
- `timezone`
- `venueId`
- `matchday`

Exemple :

```json
{
  "id": "G001",
  "group": "A",
  "homeTeamId": "mex",
  "awayTeamId": "rsa",
  "date": "2026-06-11",
  "timeLocal": "13:00",
  "timezone": "UTC-6",
  "venueId": "mexico_city",
  "matchday": 1
}
```

Pourquoi `matchday` est important :

```text
journée 1
journée 2
journée 3
phase finale
```

Il permet de mettre à jour le tournoi journée par journée.

---

### 5.4 bracketRules.json

Rôle :

```text
règles de phase finale
```

Ce fichier est critique.

Il doit gérer :

- Round of 32 ;
- vainqueurs de groupes ;
- deuxièmes de groupes ;
- huit meilleurs troisièmes ;
- propagation des vainqueurs.

Exemple :

```json
{
  "id": "M074",
  "round": "R32",
  "homeSlot": "1E",
  "awaySlot": "3A/B/C/D/F",
  "awaySlotOptions": ["3A", "3B", "3C", "3D", "3F"],
  "venue": "Boston",
  "date": "2026-06-29",
  "time": "16:30",
  "timezone": "UTC-4"
}
```

Point de vigilance :

```text
["3A", "B", "C", "D", "F"]
```

est faux.

Il faut :

```text
["3A", "3B", "3C", "3D", "3F"]
```

---

### 5.5 real_results.json

Rôle :

```text
source de vérité des scores réels
```

Exemple :

```json
[
  {
    "matchId": "G001",
    "homeTeamId": "mex",
    "awayTeamId": "rsa",
    "homeGoals": 2,
    "awayGoals": 1,
    "status": "played",
    "source": "manual",
    "updatedAt": "2026-06-11T23:00:00Z"
  }
]
```

Ce fichier sert à :

- figer les matchs joués ;
- recalculer les classements ;
- mettre à jour Elo ;
- mettre à jour FIFA ;
- relancer Monte Carlo uniquement sur les matchs restants.

---

## 6. Théorie et modèles utilisés

### 6.1 Elo : force relative

Elo attribue un rating numérique à chaque équipe.

Formule du score attendu :

```math
W_e = \frac{1}{1 + 10^{-\frac{(R_A - R_B)}{400}}}
```

Attention :

Cette formule ne donne pas directement une probabilité de victoire.

Elle donne un `expected score`.

Dans Elo :

```text
victoire = 1
nul = 0.5
défaite = 0
```

Exemple :

```text
France Elo = 2062
Allemagne Elo = 1932

diff = 130
```

Score attendu France :

```text
≈ 0.68
```

Interprétation :

```text
France est favorite,
mais cela ne signifie pas exactement 68 % de probabilité de victoire.
```

La probabilité victoire/nul/défaite sera plutôt calculée par la matrice de scores Poisson.

---

### 6.2 Mise à jour Elo après un match

Formule :

```math
R_n = R_o + K \times G \times (W - W_e)
```

où :

- `R_o` = Elo avant match ;
- `R_n` = Elo après match ;
- `K` = importance du match ;
- `G` = multiplicateur lié à la différence de buts ;
- `W` = résultat observé ;
- `W_e` = résultat attendu.

Exemple :

```text
France Elo = 2062
Canada Elo = 1780
```

Score attendu France :

```text
≈ 0.84
```

Si France gagne 3-0 :

```text
W = 1
G > 1
Elo France augmente
```

Si France fait 0-0 :

```text
W = 0.5
résultat inférieur aux attentes
Elo France diminue légèrement
```

---

### 6.3 Poisson : modélisation des buts

La loi de Poisson modélise le nombre de buts marqués par une équipe.

Formule :

```math
P(X = k) = \frac{e^{-\lambda}\lambda^k}{k!}
```

où :

- `k` = nombre de buts ;
- `λ` = moyenne attendue de buts.

Rôle :

```text
λ_A = buts moyens attendus pour l'équipe A
λ_B = buts moyens attendus pour l'équipe B
```

Poisson permet de calculer :

- P(0 but) ;
- P(1 but) ;
- P(2 buts) ;
- P(3 buts) ;
- etc.

Limites :

- suppose une indépendance approximative entre les deux scores ;
- peut mal calibrer certains petits scores ;
- ne modélise pas parfaitement les 0-0 et 1-1.

Améliorations futures :

- Dixon-Coles ;
- Bivariate Poisson ;
- Copula.

---

### 6.4 Elo-Poisson : conversion de la force en buts attendus

Le modèle Elo fournit une force.

Poisson a besoin d’un `λ`.

Nous devons donc convertir :

```text
différence Elo
↓
λ_A et λ_B
```

Formule V1 :

```math
\lambda_A = baseGoals \times e^{\frac{diff}{scale}}
```

```math
\lambda_B = baseGoals \times e^{-\frac{diff}{scale}}
```

avec :

- `diff = Elo_A - Elo_B`
- `baseGoals` = moyenne de buts attendue par équipe
- `scale` = sensibilité à l’écart Elo

Pipeline :

```text
Elo
↓
différence Elo
↓
fonction de conversion
↓
λ_A et λ_B
↓
Poisson
↓
scores
↓
Monte Carlo
```

---

### 6.5 baseGoals et scale

Point important :

- `baseGoals` ne vient pas de la théorie Elo ;
- `scale` ne vient pas de la théorie Elo ;
- ce sont des paramètres globaux ;
- ils sont communs à toutes les équipes ;
- ils ne sont pas calculés séparément pour chaque équipe ;
- les λ changent selon le match parce que `diff` change ;
- `baseGoals` et `scale` restent fixes pendant une simulation.

---

### Estimation de baseGoals

`baseGoals` correspond à la moyenne historique de buts par équipe.

Calcul :

```text
totalGoalsPerMatch = moyenne(home_score + away_score)

baseGoals = totalGoalsPerMatch / 2
```

Avec `matches_clean.csv` :

```python
import pandas as pd

df = pd.read_csv("src/data/processed/matches_clean.csv")

total_goals_per_match = (
    df["home_score"] + df["away_score"]
).mean()

baseGoals = total_goals_per_match / 2

print(baseGoals)
```

Exemple :

```text
moyenne historique = 2.70 buts par match
baseGoals = 2.70 / 2 = 1.35
```

---

### Calibration de scale

`scale` n’est pas observable directement.

C’est un hyperparamètre.

Il contrôle la sensibilité du modèle aux écarts Elo.

```text
scale faible
→ modèle agressif

scale élevé
→ modèle prudent
```

Exemples :

```text
scale = 400
→ 200 points Elo créent un gros écart de λ

scale = 1200
→ 200 points Elo créent un écart plus modéré
```

Méthode :

```text
tester scale = 400
tester scale = 600
tester scale = 800
tester scale = 1000
tester scale = 1200
```

Pour chaque valeur :

1. calculer les λ ;
2. produire les probabilités de match ;
3. comparer aux résultats historiques ;
4. mesurer Log Loss, Brier Score, Calibration Curve ;
5. garder la meilleure valeur.

---

### 6.6 Exemple Elo-Poisson complet

Supposons :

```text
France Elo = 2062
Canada Elo = 1780

diff = 282

baseGoals = 1.35
scale = 800
```

Alors :

```math
\lambda_{France} = 1.35 \times e^{282/800}
```

```text
λ_France ≈ 1.92
```

et :

```math
\lambda_{Canada} = 1.35 \times e^{-282/800}
```

```text
λ_Canada ≈ 0.95
```

Interprétation :

```text
France : 1.92 buts attendus
Canada : 0.95 but attendu
```

Ensuite Poisson donne :

```text
P(France marque 0)
P(France marque 1)
P(France marque 2)

P(Canada marque 0)
P(Canada marque 1)
P(Canada marque 2)
```

Puis on construit une matrice :

| Score | Probabilité |
|---|---|
| 0-0 | P(FRA=0) × P(CAN=0) |
| 1-0 | P(FRA=1) × P(CAN=0) |
| 2-0 | P(FRA=2) × P(CAN=0) |
| 2-1 | P(FRA=2) × P(CAN=1) |

La somme des scores où :

```text
France > Canada
```

donne :

```text
P(victoire France)
```

La somme des scores où :

```text
France = Canada
```

donne :

```text
P(nul)
```

La somme des scores où :

```text
France < Canada
```

donne :

```text
P(victoire Canada)
```

---

## 7. Versions du modèle

### 7.1 V1 : Elo + Poisson + Monte Carlo

La V1 est la baseline.

Elle utilise :

```text
strength = Elo
```

Pipeline :

```text
Elo
↓
différence Elo
↓
λ_A et λ_B
↓
Poisson
↓
scores
↓
Monte Carlo
```

Avantages :

- simple ;
- rapide ;
- interprétable ;
- peu de dépendances ;
- excellent point de départ.

Limites :

- la relation Elo → λ est imposée manuellement ;
- `baseGoals` et `scale` doivent être calibrés ;
- ne tient pas compte des points FIFA ;
- ne tient pas compte de la forme récente.

---

### 7.2 V1.5 : Elo + FIFA

Objectif :

```text
ajouter FIFA comme signal complémentaire
```

Attention :

Elo et FIFA ne sont pas sur la même échelle.

Donc il ne faut pas faire :

```text
strength = 0.8 × Elo + 0.2 × FIFA
```

directement.

Il faut normaliser :

```math
strength =
\alpha \times Elo_{norm}
+
(1-\alpha)\times FIFA_{norm}
```

Méthodes possibles :

- Z-score ;
- Min-Max scaling.

Exemple :

```text
France :
Elo = 2062
FIFA = 1877

Allemagne :
Elo = 1932
FIFA = 1716
```

Après normalisation :

```text
France = 1.75
Allemagne = 1.20
```

Avec :

```text
α = 0.8
```

Elo reste dominant, mais FIFA influence légèrement la force finale.

---

### 7.3 V2 : Elo + FIFA + tendances

Objectif :

```text
ajouter la dynamique récente des équipes
```

Variables possibles :

- `pointsTrend3Months`
- `pointsTrend12Months`
- `rankingTrend3Months`
- `rankVolatility`

Les tendances basées sur les points sont préférables aux tendances basées sur le rang.

Formule possible :

```math
trendScore =
w_1 \times pointsTrend3Months
+
w_2 \times pointsTrend12Months
-
w_3 \times rankVolatility
```

Puis :

```math
strength_{final}
=
strength_{hybrid}
+
trendScore
```

Exemple :

```text
Espagne :
pointsTrend3Months = +25
pointsTrend12Months = +45
rankVolatility = 2
```

Avec :

```text
w1 = 0.4
w2 = 0.5
w3 = 0.2
```

```text
trendScore ≈ 32.1
```

La force de l’Espagne augmente légèrement.

---

### 7.4 V3 : Live Dynamic Update

Objectif :

```text
mettre à jour les forces pendant le tournoi
```

Deux updates :

```text
update Elo
update FIFA
```

Formule Elo :

```math
R_n = R_o + K \times G \times (W-W_e)
```

Formule FIFA simplifiée :

```math
P_{new}=P_{before}+I\times(W-W_e)
```

Pipeline :

```text
score réel
↓
match figé
↓
update Elo
↓
update FIFA
↓
nouvelle force
↓
Monte Carlo sur matchs restants
```

Exemple :

```text
Argentine bat Canada
```

Alors :

```text
Argentine Elo augmente
Canada Elo baisse

Argentine FIFA Points augmente légèrement
Canada FIFA Points baisse
```

Cette version sert principalement au mode live.

---

### 7.5 V4 : Poisson régressif

Objectif :

```text
laisser les données apprendre directement les λ
```

Dans V1 :

```text
Elo
↓
fonction définie manuellement
↓
λ
```

Dans V4 :

```text
Elo
+
FIFA
+
historique
+
domicile
+
confédération
+
forme récente
↓
régression de Poisson
↓
λ appris
```

Forme possible :

```math
\lambda =
e^{
\beta_0
+
\beta_1 Elo_{team}
+
\beta_2 Elo_{opponent}
+
\beta_3 Home
+
...
}
```

Les coefficients `β` sont appris sur l’historique.

Avantages :

- plus piloté par les données ;
- plus flexible ;
- potentiellement plus performant.

Limites :

- plus complexe ;
- moins interprétable ;
- dépend fortement de la qualité des features ;
- nécessite davantage de calibration.

---

### 7.6 V5 : modèles avancés de score

Objectif :

```text
corriger l’hypothèse d’indépendance des scores
```

Modèles possibles :

- Dixon-Coles ;
- Bivariate Poisson ;
- Copula.

Utilité :

- meilleure modélisation des 0-0 ;
- meilleure modélisation des 1-1 ;
- meilleure calibration des faibles scores.

---

## 8. Monte Carlo

Principe :

```text
répéter le tournoi N fois
```

À chaque simulation :

1. simuler les scores ;
2. calculer les classements ;
3. sélectionner les qualifiés ;
4. construire le bracket ;
5. simuler la phase finale ;
6. enregistrer les résultats.

Sorties :

- probabilité de qualification ;
- probabilité d’atteindre les 8es ;
- probabilité d’atteindre les quarts ;
- probabilité d’atteindre les demies ;
- probabilité d’atteindre la finale ;
- probabilité d’être champion.

Exemple :

```text
10 000 simulations
France champion 1 800 fois
```

Probabilité :

```text
1 800 / 10 000 = 18 %
```

Erreur approximative :

```text
1 000 simulations  → ~3 %
10 000 simulations → ~1 %
100 000 simulations → ~0.3 %
```

Pour la V1 :

```text
10 000 simulations suffisent généralement
```

---

## 9. Calibration et évaluation

Un modèle n’est pas bon parce qu’il produit des prédictions.

Il est bon s’il est calibré.

Exemple :

```text
si le modèle annonce 70 %
sur 100 événements similaires
alors environ 70 doivent se produire
```

Données :

```text
martj42 international_results
src/data/processed/matches_clean.csv
```

Métriques :

- Log Loss ;
- Brier Score ;
- Calibration Curve ;
- Reliability Diagram.

À calibrer :

- `baseGoals`
- `scale`
- `alpha`
- poids des tendances
- choix du modèle de score

Objectif :

```text
V1 vs V1.5 vs V2 vs V3 vs V4
```

On conserve uniquement les ajouts qui améliorent réellement :

- Log Loss ;
- Brier Score ;
- calibration ;
- cohérence des probabilités de tournoi.

---

## 10. Live update : conception

### 10.1 Modules live

```text
src/domain/live/
  load_real_results.py
  freeze_matches.py
  group_standings.py
  points_update.py
  update_fifa_rating_after_result.py
  live_state.py
```

---

### 10.2 load_real_results.py

Rôle :

```text
charger et valider real_results.json
```

Vérifie :

- présence de `matchId` ;
- présence des équipes ;
- scores valides ;
- statut valide ;
- correspondance avec `groupMatches.json`.

---

### 10.3 freeze_matches.py

Rôle :

```text
figer les matchs déjà joués
```

Comportement :

- un match `played` n’est plus simulé ;
- son score est conservé ;
- il sert au classement ;
- il sert aux updates Elo/FIFA.

---

### 10.4 group_standings.py

Rôle :

```text
recalculer les classements de groupe
```

Règles de base :

```text
victoire = 3 points
nul = 1 point
défaite = 0 point
```

Colonnes calculées :

- played ;
- wins ;
- draws ;
- losses ;
- goalsFor ;
- goalsAgainst ;
- goalDifference ;
- points.

Départages MVP :

1. points ;
2. différence de buts ;
3. buts marqués ;
4. choix manuel ou fair-play.

---

### 10.5 points_update.py

Rôle :

```text
mettre à jour les Elo après résultats réels
```

Utilise :

```math
R_n = R_o + K \times G \times (W-W_e)
```

---

### 10.6 update_fifa_rating_after_result.py

Rôle :

```text
mettre à jour les points FIFA
```

Utilise :

```math
P_{new}=P_{before}+I\times(W-W_e)
```

Attention :

Cette mise à jour est une approximation fondée sur la documentation publique FIFA.

---

### 10.7 live_state.py

Rôle :

```text
construire l’état courant du tournoi
```

Contient :

- matchs joués ;
- matchs restants ;
- classements ;
- équipes ;
- Elo actualisés ;
- FIFA Points actualisés ;
- bracket partiel si phase finale commencée.

---

## 11. Simulation : conception technique

Dossier :

```text
src/domain/simulation/
```

Fichiers :

```text
poisson_model.py
simulate_match.py
simulate_tournament.py
run_monte_carlo.py
```

---

### 11.1 poisson_model.py

Rôle :

```text
convertir Elo en λ
```

Entrées :

- Elo équipe A ;
- Elo équipe B ;
- `baseGoals` ;
- `scale`.

Sorties :

```text
lambdaA
lambdaB
score probabilities
match probabilities
```

---

### 11.2 simulate_match.py

Rôle :

```text
simuler un score
```

Deux modes :

```text
mode distribution
→ retourne toutes les probabilités de score

mode random
→ tire un score aléatoire
```

---

### 11.3 simulate_tournament.py

Rôle :

```text
simuler un tournoi complet
```

Étapes :

1. charger équipes ;
2. charger groupes ;
3. charger matchs ;
4. appliquer résultats réels si disponibles ;
5. simuler matchs restants ;
6. calculer classements ;
7. sélectionner qualifiés ;
8. construire bracket ;
9. simuler phase finale ;
10. retourner parcours.

---

### 11.4 run_monte_carlo.py

Rôle :

```text
répéter simulate_tournament N fois
```

Sorties :

```json
{
  "fra": {
    "roundOf32": 0.91,
    "quarterFinal": 0.58,
    "semiFinal": 0.35,
    "final": 0.21,
    "champion": 0.13
  }
}
```

---

## 12. Tests indispensables

### 12.1 Tests données

- tous les IDs de `groups.json` existent dans `teams.json` ;
- tous les IDs de `groupMatches.json` existent dans `teams.json` ;
- toutes les équipes du tournoi ont un Elo ;
- `groupMatches.json` contient bien `matchday` ;
- `bracketRules.json` a des `awaySlotOptions` propres ;
- `venues.json` contient les stades attendus.

---

### 12.2 Tests modèle

- Poisson retourne des probabilités positives ;
- la somme des probabilités de score est proche de 1 ;
- une équipe plus forte a un λ plus élevé ;
- si `diff = 0`, alors `lambdaA = lambdaB = baseGoals` ;
- si `scale` augmente, l’écart entre λ diminue.

---

### 12.3 Tests live

- un match joué est figé ;
- un match joué n’est jamais resimulé ;
- les classements se mettent à jour ;
- Elo se met à jour après résultat ;
- FIFA se met à jour après résultat ;
- Monte Carlo ne simule que les matchs restants.

---

### 12.4 Tests tournoi

- classement de groupe simple ;
- égalité aux points ;
- égalité à la différence de buts ;
- sélection des 8 meilleurs troisièmes ;
- construction correcte du Round of 32 ;
- propagation des vainqueurs ;
- changement de vainqueur nettoie les tours suivants.

---

## 13. Priorités immédiates

### Priorité 1 : [validation des données](remarques\priorites\priorite_1_validation.md) ok

Vérifier :

```text
teams.json
groups.json
groupMatches.json
bracketRules.json
venues.json
```

Objectif :

```text
aucun ID non résolu
aucun Elo manquant
aucun slot de bracket mal parsé
```

---

### Priorité 2 : [modèle Poisson](remarques\priorites\priorite_2_poisson.md) ok
Créer :

```text
src/domain/simulation/poisson_model.py
```

Fonctions :

```text
compute_lambdas()
poisson_pmf()
score_matrix()
match_probabilities()
```

---

### Priorité 3 : [simulation d’un match](remarques\priorites\priorite_3_simulation.md) ok

Créer :

```text
src/domain/simulation/simulate_match.py
```

Fonctions :

```text
predict_match()
sample_match_score()
```

---

### Priorité 4 : [moteur tournoi](remarques/priorites/priorite_4_moteur_tournoi.md)

Créer :

```text
src/domain/tournament/
  compute_group_standings.py
  rank_third_placed.py
  build_bracket.py
```

---

### Priorité 5 : [Monte Carlo](remarques\priorites\priorite_5_monte_carlo.md)

Créer :

```text
src/domain/simulation/run_monte_carlo.py
```

---

---

### Priorité 6 : Live Update (Les fondations du direct)

L'objectif est d'injecter la réalité dans la simulation pour mettre à jour les statistiques au fil de la compétition.

Créer :

```text
src/data/raw/real_results.json
```

Modifier le simulateur pour qu'il force les résultats existants (au lieu de les simuler via Poisson) et génère une photographie des probabilités à un instant T (ex: `snapshot_day0.json`).

---

### Priorité 7 : Delta Tracker (La comparaison dynamique)

Créer l'outil d'analyse qui compare deux "photographies" du Monte Carlo pour afficher l'évolution des chances de chaque équipe (les deltas).

Créer :

```text
src/domain/evaluation/
  compare_snapshots.py
```

*Ceci permet de répondre à la question : "Quel est l'impact de cette défaite surprise sur les chances de l'Argentine ?"*

---

### Priorité 8 : Calibration & Évaluation (Le juge de paix)

Avant de complexifier le modèle, nous devons calculer sa précision mathématique (Brier Score, Log Loss) sur un jeu de données de référence (ex: Coupe du Monde 2022).

Créer :

```text
src/domain/evaluation/
  log_loss.py
  brier_score.py
  calibration_curve.py
```

---

### Priorité 9 : V1.5 et V2 (L'amélioration continue)

Le principe central du projet est :
> **Ajouter de la complexité uniquement si elle améliore la calibration.**

1. **V1.5** : `Elo + FIFA normalisé`
2. **V2** : `Elo + FIFA + tendances`

Utiliser le module de calibration (Priorité 8) pour vérifier si la V1.5 est mathématiquement meilleure que la V1. Si oui, on la garde. Si non, on la rejette.

## 14. Ce qui est déjà réalisé

- pipeline d’acquisition ;
- normalisation FIFA ;
- intégration Elo manuel ;
- traçabilité de l’Elo ;
- fichiers normalisés de base ;
- alias équipes ;
- premiers fichiers OpenFootball ;
- historique martj42 ;
- vision claire des modèles.

---

## 15. Ce qui manque encore

- moteur Elo-Poisson ;
- moteur Monte Carlo ;
- moteur live ;
- vrai `real_results.json` ;
- calibration automatique de `baseGoals` ;
- calibration de `scale` ;
- tests complets ;
- validation forte du bracket 2026.

---

## 16. Conclusion



Ce document doit rester la référence centrale du projet.

Toutes les décisions techniques doivent s’aligner sur cette logique :

```text
simple
testable
calibré
évolutif
explicable
```
---