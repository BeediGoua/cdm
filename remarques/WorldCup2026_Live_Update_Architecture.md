# Simulateur probabiliste Coupe du Monde 2026 avec live update

Un simulateur probabiliste de Coupe du Monde 2026 combinant règles officielles FIFA, moteur de bracket, prédiction de scores par modèle Elo-Poisson, simulation Monte Carlo et mise à jour progressive pendant le tournoi.

C’est propre, sérieux, mais pas trop compliqué.

La FIFA doit servir pour le format, les groupes, le calendrier et les stades.

Les ratings Elo peuvent venir de World Football Elo Ratings ou d’un site miroir comme international-football.net.

Pour les matchs historiques, on peut utiliser le dataset Kaggle “International football results”, qui contient des dizaines de milliers de matchs internationaux depuis 1872.

Les PDF récupérés ne sont pas la vérité officielle. Ils servent à comprendre:

```text
logique UX
structure du simulateur
gestion des barragistes
bracket
meilleurs troisièmes
propagation des vainqueurs
```

## Ajout live

Le simulateur doit pouvoir fonctionner en deux temps:

```text
avant tournoi:
  simulation complète pré-tournoi

pendant tournoi:
  scores réels renseignés après chaque journée
  matchs joués fixés
  classements recalculés
  Monte Carlo relancé sur les matchs restants
```

# 3. Architecture réajustée

On garde une architecture propre, mais moins lourde.

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
    live/
  features/
    setup/
    predictor/
    bracket/
    dashboard/
    live-update/
  components/
    ui/
    football/
  store/
  services/
  tests/
```

Pas besoin de créer trop tôt:

```text
monitoring/
supabase/
charts/
venue-map/
advanced-models/
```

On les garde pour plus tard.

## Ajout

On ajoute `live/` et `live-update/` car ce n’est pas une feature cosmétique: c’est une vraie évolution du moteur.

# 4. Données: où les chercher et où les mettre

## src/data/raw/

Ici, on stocke les données brutes, proches de leur source.

```text
src/data/raw/fifa_groups.json
src/data/raw/fifa_schedule.json
src/data/raw/fifa_venues.json
src/data/raw/elo_ratings.json
src/data/raw/historical_results.csv
src/data/raw/real_results.json
```

Sources:

```text
FIFA: groupes, calendrier, stades, règles
World Football Elo Ratings: force des équipes
Kaggle/GitHub: résultats historiques
PDF récupérés: logique UX, brouillon des groupes, bracket, barragistes
Saisie utilisateur: scores réels après chaque journée
```

Les PDF ne doivent pas être la source de vérité. Ils servent à comprendre comment le site est construit.

## src/data/normalized/teams.json

Contenu:

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

Source:

```text
noms et qualification: FIFA
Elo: World Football Elo Ratings
fifaRank: FIFA Ranking officiel
flagCode: mapping manuel
```

## src/data/normalized/groups.json

```json
{
  "A": ["mex", "rsa", "kor", "playoff_uefa_d"],
  "B": ["can", "playoff_uefa_a", "qat", "sui"]
}
```

Source:

```text
FIFA Final Draw
```

Le PDF peut servir à pré-remplir, mais il faut vérifier avec FIFA.

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
    "venueId": "azteca",
    "matchday": 1
  }
]
```

Source:

```text
FIFA match schedule
```

## Ajout important

Il faut ajouter `matchday`.

Pourquoi ?

Parce que cela permet de renseigner les résultats:

```text
journée 1
journée 2
journée 3
phase finale
```

Donc `matchday` sert directement au live update.

## src/data/normalized/bracketRules.json

C’est le fichier le plus sensible.

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

Source:

```text
FIFA + vérification avec les PDF
```

Ici, il faut faire des tests, car une erreur dans les meilleurs troisièmes rend tout le simulateur faux.

## Nouveau fichier: src/data/normalized/realResults.json

Contenu:

```json
[
  {
    "matchId": "M001",
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

But:

```text
stocker les scores réels renseignés après chaque journée
```

Ce fichier est optionnel au départ, mais nécessaire pour la version live.

# 5. Moteur tournoi

## domain/tournament/computeGroupStandings.ts

But:

```text
calculer les classements de groupe
```

Formule:

```text
points = 3 × victoires + 1 × nuls
différence = buts marqués - buts encaissés
```

Sortie:

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

## Ajout live

Cette fonction doit accepter deux types de matchs:

```text
matchs réels déjà joués
matchs simulés
```

Donc elle ne doit pas dépendre de l’interface, seulement d’une liste de résultats.

## domain/tournament/tiebreakers.ts

Pour le MVP:

```text
points
différence de buts
buts marqués
fair-play ou choix manuel
```

Version avancée:

```text
confrontations directes
différence de buts entre équipes concernées
buts marqués entre équipes concernées
fair-play
tirage au sort
```

## domain/tournament/rankThirdPlacedTeams.ts

But:

```text
prendre les 12 troisièmes et sélectionner les 8 meilleurs
```

Tri:

```text
points
différence de buts
buts marqués
fair-play
```

## domain/tournament/buildBracket.ts

But:

```text
construire le tableau final à partir des slots 1A, 2A, 3A...
```

## domain/tournament/propagateWinner.ts

But:

```text
envoyer le vainqueur au tour suivant
nettoyer les tours suivants si on change un résultat
```

## Ajout live

Si un match de phase finale est déjà joué réellement, son vainqueur doit être fixé et non modifiable dans les simulations.

# 6. Modèle probabiliste simple

On ne part pas directement sur Dixon-Coles. Trop lourd pour le MVP.

On fait:

```text
Elo + Poisson
```

## domain/prediction/teamStrength.ts

But:

```text
transformer une équipe en force numérique
```

Version simple:

```text
strength(team) = elo(team)
```

## Ajout live

En V2, cette fonction pourra utiliser:

```text
elo initial
ou
elo mis à jour après les scores réels
```

Donc elle doit pouvoir recevoir un objet:

```ts
updatedRatings?: Record<string, number>
```

## domain/prediction/expectedGoals.ts

But:

```text
calculer le nombre moyen de buts attendus
```

Formule simple:

```text
diff = eloA - eloB
lambdaA = baseGoals × exp(diff / scale)
lambdaB = baseGoals × exp(-diff / scale)
```

Exemple:

```ts
const baseGoals = 1.35
const scale = 800
lambdaA = baseGoals * Math.exp(diff / scale)
lambdaB = baseGoals * Math.exp(-diff / scale)
```

Interprétation:

```text
si A est plus fort, lambdaA augmente
si B est plus faible, lambdaB diminue
lambda reste toujours positif grâce à exp()
```

## domain/prediction/scoreDistribution.ts

But:

```text
calculer P(scoreA = x, scoreB = y)
```

Formule Poisson:

```text
P(X = k) = exp(-lambda) × lambda^k / k!
```

Pour un score:

```text
P(A=x, B=y) = P_Poisson(x; lambdaA) × P_Poisson(y; lambdaB)
```

Hypothèse simple:

```text
les buts des deux équipes sont indépendants
```

Limite:

```text
les petits scores comme 0-0, 1-0, 1-1 peuvent être mal calibrés
```

C’est là que Dixon-Coles pourra venir plus tard.

## domain/prediction/predictMatch.ts

But:

```text
sortir les probabilités victoire / nul / défaite
```

Il agrège les probabilités de score:

```text
P(A gagne) = somme P(x,y) pour x > y
P(nul) = somme P(x,y) pour x = y
P(B gagne) = somme P(x,y) pour x < y
```

# 7. Simulation Monte Carlo

## domain/simulation/simulateMatch.ts

But:

```text
tirer un score aléatoire selon la distribution Poisson
```

## domain/simulation/simulateTournament.ts

But:

```text
simuler une Coupe du monde complète
```

Étapes:

```text
1. simuler tous les matchs de groupe
2. calculer les classements
3. sélectionner les 8 meilleurs troisièmes
4. construire le bracket
5. simuler les matchs à élimination directe
6. retourner champion + parcours de chaque équipe
```

## Ajout live

La simulation doit accepter un état courant:

```ts
type TournamentState = {
  realResults: RealMatchResult[]
  updatedRatings?: Record<string, number>
}
```

Donc les étapes deviennent:

```text
1. fixer les matchs déjà joués
2. simuler uniquement les matchs restants
3. recalculer les classements avec réel + simulé
4. construire le bracket à partir de l’état obtenu
5. fixer les matchs de phase finale déjà joués
6. simuler les matchs restants
7. retourner champion + parcours
```

## domain/simulation/runMonteCarlo.ts

But:

```text
répéter N tournois
```

Formule:

```text
P(champion = équipe i) = nombre de titres de i / N
```

Erreur Monte Carlo:

```text
erreur ≈ 1 / sqrt(N)
```

Donc:

```text
1 000 simulations: rapide, bruité
10 000 simulations: bon compromis
100 000 simulations: plus stable, plus lent
```

Pour ton MVP, je recommande:

```text
10 000 simulations
```

## Ajout live

On utilisera la même fonction `runMonteCarlo.ts`, mais avec deux modes:

```text
pré-tournoi:
  aucun match réel

pendant tournoi:
  certains matchs déjà fixés
```

# 8. Évaluation: version simple mais sérieuse

On ne fait pas une usine à gaz.

On ajoute juste:

```text
backtest simple
log loss
calibration basique
```

## domain/evaluation/backtest.ts

Idée:

```text
entraîner ou régler le modèle sur les matchs avant 2022
tester sur Coupe du Monde 2022
```

## domain/evaluation/logLoss.ts

Formule:

```text
LogLoss = - moyenne(log(probabilité attribuée au résultat réel))
```

Si le modèle dit:

```text
France gagne: 70 %
Nul: 20 %
Maroc gagne: 10 %
```

et que France gagne, la perte est:

```text
-log(0.70)
```

Plus c’est petit, mieux c’est.

## domain/evaluation/calibration.ts

But:

```text
vérifier si les probabilités sont réalistes
```

Exemple:

```text
quand le modèle donne 70 % de victoire, l’équipe gagne-t-elle environ 70 % du temps ?
```

C’est un excellent signal de sérieux.

## Ajout live

La calibration dynamique complète n’est pas prioritaire.

Pourquoi ?

```text
le tournoi contient peu de matchs
réentraîner un modèle complet après chaque journée serait instable
```

Donc on ne dit pas:

```text
le modèle se réentraîne automatiquement
```

On dit plutôt:

```text
le modèle se met à jour progressivement via les scores réels et éventuellement un update Elo.
```

# 9. Nouveau module live update

Ce module est l’ajout principal.

## Objectif

Permettre au simulateur d’être utilisé pendant la Coupe du Monde.

Après chaque journée:

```text
l’utilisateur renseigne les scores réels
les matchs joués sont fixés
les classements sont recalculés
les probabilités sont recalculées
Monte Carlo est relancé sur les matchs restants
```

## domain/live/applyRealResult.ts

But:

```text
ajouter ou modifier un résultat réel
```

Entrée:

```json
{
  "matchId": "M001",
  "homeGoals": 2,
  "awayGoals": 1
}
```

Sortie:

```text
état du tournoi mis à jour
```

## domain/live/getPlayedMatches.ts

But:

```text
retourner les matchs déjà joués
```

## domain/live/getRemainingMatches.ts

But:

```text
retourner les matchs encore à simuler
```

## domain/live/updateLiveStandings.ts

But:

```text
recalculer les classements avec les résultats réels
```

## domain/live/updateEloAfterResult.ts

But:

```text
ajuster la force des équipes après un résultat réel
```

Formule:

```text
R_new = R_old + K × (S - E)
```

Avec:

```text
S = 1 si victoire
S = 0.5 si nul
S = 0 si défaite
E = 1 / (1 + 10^(-(R_A - R_B)/400))
```

Interprétation:

```text
si une équipe faible bat une équipe forte, son Elo augmente fortement
si une équipe forte bat une équipe faible, son Elo augmente peu
si une équipe forte perd, son Elo baisse fortement
```

## domain/live/resimulateFromCurrentState.ts

But:

```text
relancer Monte Carlo depuis l’état actuel du tournoi
```

Il doit prendre en compte:

```text
matchs déjà joués
classements partiels
ratings éventuellement mis à jour
phase finale partiellement jouée
```

# 10. Interface: version réajustée

On garde 4 pages, mais simples.

## Page 1: Setup

```text
choisir barragistes
voir groupes
voir calendrier
```

## Page 2: Predictions

```text
auto-remplir les matchs avec le modèle
modifier les scores manuellement
voir classements
```

## Page 3: Bracket

```text
voir tableau final
simuler ou choisir les vainqueurs
afficher champion
```

## Page 4: Dashboard

```text
probabilités par équipe
probabilité champion
probabilité finale
probabilité demi-finale
```

## Ajout

## Page 5: Live Update

```text
renseigner les scores réels par journée
valider les matchs joués
recalculer les classements
relancer Monte Carlo
voir les variations de probabilités
```

Composants:

```text
MatchdayInput.tsx
LiveResultsTable.tsx
LiveProbabilityShift.tsx
```

Pas besoin de:

```text
comparer 10 scénarios
carte des stades
Supabase
PWA
monitoring visuel
```

au début.

# 11. Structure finale réécrite

```text
src/
  data/
    raw/
      fifa_groups.json
      fifa_schedule.json
      fifa_venues.json
      elo_ratings.json
      historical_results.csv
      real_results.json

    normalized/
      teams.json
      groups.json
      playoffs.json
      groupMatches.json
      venues.json
      bracketRules.json
      realResults.json

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

    live/
      applyRealResult.ts
      getPlayedMatches.ts
      getRemainingMatches.ts
      updateLiveStandings.ts
      updateEloAfterResult.ts
      resimulateFromCurrentState.ts
      live.types.ts

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

    live-update/
      MatchdayInput.tsx
      LiveResultsTable.tsx
      LiveProbabilityShift.tsx

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

  store/
    tournamentStore.ts
    predictionStore.ts
    liveStore.ts

  tests/
    tournament/
    prediction/
    simulation/
    live/
```

# 12. Ce qu’il faut chercher concrètement

Sources prioritaires:

```text
1. FIFA World Cup 2026 final draw results
2. FIFA World Cup 2026 match schedule fixtures stadiums
3. FIFA World Cup 2026 groups tie-breakers
4. FIFA scores fixtures page
5. World Football Elo Ratings
6. FIFA/Coca-Cola Men's World Ranking
7. Kaggle international football results
8. GitHub martj42 international_results
```

FIFA Ranking utilise aussi une méthode Elo pour son classement masculin, ce qui peut servir de comparaison secondaire avec World Football Elo Ratings.

Le dépôt GitHub martj42/international_results décrit un fichier results.csv avec les résultats de matchs internationaux masculins, utile si tu veux éviter de dépendre uniquement de Kaggle.

## Ajout live

Pendant le tournoi, il faudra aussi utiliser:

```text
FIFA scores fixtures page
```

pour récupérer ou vérifier les scores réels.

Si on ne fait pas d’import automatique au début, on pourra simplement saisir les scores manuellement dans la page Live Update.

# 13. Version finale sérieuse

Donc oui, on réécrit.

La version correcte est:

```text
MVP = règles FIFA + bracket + Elo-Poisson + Monte Carlo + dashboard simple
V1.5 = saisie des scores réels par journée + Monte Carlo sur matchs restants
V2 = backtest + calibration + scénarios + update Elo après scores réels
V3 = Dixon-Coles + xG + fatigue + blessures + monitoring
```

C’est le bon niveau: assez sérieux pour montrer une vraie démarche data science, mais pas trop compliqué au point de ne jamais finir.

# 14. Phrase finale du projet

Le simulateur peut être utilisé avant et pendant la Coupe du Monde. Avant le tournoi, il estime les probabilités à partir des forces Elo et du modèle Elo-Poisson. Pendant le tournoi, l’utilisateur renseigne les scores réels après chaque journée; le système fixe les matchs déjà joués, recalcule les classements, met éventuellement à jour les ratings Elo, puis relance Monte Carlo sur les matchs restants afin d’obtenir les nouvelles probabilités de qualification, de finale et de victoire finale.

Cette version montre:

```text
règles métier solides
modélisation probabiliste
simulation Monte Carlo
mise à jour progressive
ingénierie logicielle propre
évaluation minimale
roadmap réaliste
```
