Oui, ça change notre recap. Le projet est maintenant plus solide : on ne dépend plus seulement de FIFA + Elo manuel. On a maintenant un vrai socle V1.

Rappel du projet

Nous voulons construire un simulateur probabiliste de Coupe du Monde 2026 :

données tournoi
+ FIFA Ranking
+ Elo
+ Poisson
+ Monte Carlo
+ live update

Objectif final :

estimer les probabilités de qualification, huitièmes, quarts, demies, finale et victoire finale

Le format officiel 2026 est bien un tournoi à 48 équipes, 12 groupes, les deux premiers de chaque groupe et les 8 meilleurs troisièmes qualifiés pour le Round of 32.  

⸻

Ce qui a changé récemment

Avant, notre socle était :

FIFA Ranking API
+ martj42 historical results
+ Elo manuel
+ données tournoi FIFA manuelles

Maintenant, il devient :

FIFA Ranking API
+ FootballRatings Elo
+ OpenFootball 2026
+ martj42 historical results
+ Elo manuel fallback

C’est une vraie amélioration.

FootballRatings donne déjà les meilleurs Elo actuels, par exemple Spain 2155, Argentina 2113/2114, France 2062, England 2020/2021, Brazil autour de 1988/1991 selon la source consultée.  

OpenFootball fournit des données publiques libres pour les Coupes du monde, y compris 2026, et l’écosystème OpenFootball propose aussi des conversions vers JSON/CSV.  

⸻

V1 : version sérieuse mais réaliste

Objectif V1

Construire une première version fonctionnelle :

structure tournoi
+ force équipe
+ prédiction de score
+ simulation Monte Carlo
+ dashboard simple

La V1 doit répondre à :

France a combien de chances d’être championne ?
Sénégal a combien de chances de sortir du groupe ?
Quel est le score probable de France - Norvège ?
Quelle équipe est favorisée dans chaque groupe ?

Sources V1

FIFA Ranking API
FootballRatings.org
OpenFootball 2026
martj42 international_results
Elo manuel fallback

FIFA Ranking sert pour les rangs, points, confédérations et drapeaux. La FIFA indique que son classement masculin utilise une méthode de type Elo, donc c’est cohérent avec notre logique de ratings.  

OpenFootball sert à récupérer ou vérifier :

cup.txt
cup_finals.txt
cup_stadiums.csv
quali_playoffs.txt

FootballRatings sert à récupérer l’Elo actuel.

martj42 sert à nettoyer l’historique et évaluer le modèle.

⸻

Données V1 à produire

src/data/raw/fifa_rankings_current.json
src/data/raw/footballratings_elo.csv
src/data/raw/openfootball_cup.txt
src/data/raw/openfootball_cup_finals.txt
src/data/raw/openfootball_stadiums.csv
src/data/raw/openfootball_quali_playoffs.txt
src/data/raw/historical_results.csv
src/data/raw/shootouts.csv
src/data/raw/goalscorers.csv
src/data/raw/elo_ratings_manual.json

Puis normaliser vers :

src/data/normalized/teams.json
src/data/normalized/groups.json
src/data/normalized/playoffs.json
src/data/normalized/groupMatches.json
src/data/normalized/venues.json
src/data/normalized/bracketRules.json

Et nettoyer :

src/data/processed/matches_clean.csv

Le fichier central est :

teams.json

Il fusionne :

FIFA Ranking
+ FootballRatings Elo
+ Elo manuel fallback
+ groupe
+ drapeau
+ confédération

Exemple :

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
  "eloSource": "footballratings.org",
  "eloDate": "2026-06-08",
  "flagUrl": "https://api.fifa.com/api/v3/picture/flags-sq-2/FRA"
}

⸻

Feature vector de base

Ce que tu appelles probablement “chess vector”, dans notre cas, c’est plutôt le feature vector : les variables qui décrivent une équipe ou un match.

Pour un match A vs B, notre feature vector V1 peut être :

elo_A
elo_B
elo_diff
fifa_rank_A
fifa_rank_B
fifa_points_A
fifa_points_B
fifa_points_diff
confederation_A
confederation_B
neutral
match_importance

Exemple :

{
  "teamA": "fra",
  "teamB": "sen",
  "eloA": 2062,
  "eloB": 1760,
  "eloDiff": 302,
  "fifaPointsA": 1877.32,
  "fifaPointsB": 1620.0,
  "fifaPointsDiff": 257.32,
  "neutral": true,
  "matchImportance": "world_cup_group"
}

Ce vecteur sert dans :

teamStrength.ts
expectedGoals.ts
predictMatch.ts
simulateMatch.ts

⸻

Formule Elo

Elo sert à mesurer la force sportive principale.

R_n=R_o+K\times G\times(W-W_e)

Avec :

Rn = nouveau Elo
Ro = ancien Elo
K = importance du match
G = multiplicateur différence de buts
W = résultat observé
We = résultat attendu

Résultat attendu :

W_e=\frac{1}{10^{-dr/400}+1}

avec :

dr = Elo_A - Elo_B

Cette formule sert dans :

updateEloAfterResult.ts

Utilisation live :

résultat réel
→ update Elo
→ nouveau teamStrength
→ nouveau Monte Carlo

Les systèmes Elo football modifient généralement l’Elo avec l’importance du match, l’avantage domicile et la marge de victoire.  

⸻

Formule FIFA

La formule FIFA est proche d’Elo :

P_{new}=P_{before}+I\times(W-W_e)

Avec :

Pbefore = points FIFA avant match
I = importance du match
W = résultat observé
We = résultat attendu

Important :

FIFA Ranking ne remplace pas Elo.

Rôle :

FIFA Points = force officielle complémentaire
Elo = force principale prédictive
Poisson = génération des scores
Monte Carlo = simulation du tournoi

⸻

Modèle de score : Elo-Poisson

Le modèle V1 doit rester simple.

On part de :

diff = Elo_A - Elo_B

Puis :

lambda_A = baseGoals × exp(diff / scale)
lambda_B = baseGoals × exp(-diff / scale)

Avec par exemple :

baseGoals = 1.35
scale = 800

Ensuite :

P(X=k)=e^{-\lambda}\frac{\lambda^k}{k!}

Puis :

P(score A=x, B=y)
=
Poisson(x, lambda_A) × Poisson(y, lambda_B)

On agrège :

P(A gagne) = somme des P(x,y) où x > y
P(nul) = somme des P(x,y) où x = y
P(B gagne) = somme des P(x,y) où x < y

⸻

Monte Carlo

Monte Carlo simule beaucoup de Coupes du Monde.

1 simulation = une Coupe du Monde complète
10 000 simulations = distribution de scénarios

Résultat :

France championne : 14.8 %
Espagne finale : 22.3 %
Sénégal sort du groupe : 51.0 %

Erreur Monte Carlo approximative :

erreur ≈ 1 / sqrt(N)

Donc :

1 000 simulations = rapide mais bruité
10 000 simulations = bon compromis
100 000 simulations = plus stable mais plus lent

⸻

V1.5 : amélioration data

But

Rendre la V1 plus automatique.

À faire :

améliorer le parser FootballRatings
récupérer plus que les 12 premières équipes
normaliser OpenFootball en JSON propre
construire automatiquement teams.json

Nouvelle règle :

FootballRatings = source Elo prioritaire
Elo manuel = fallback

OpenFootball pourra produire :

groupMatches.json
venues.json
bracketRules.json
playoffs.json

OpenFootball quick-starter peut aussi convertir les fichiers Football.TXT vers JSON ou CSV avec fbtxt2json et fbtxt2csv, ce qui peut éviter d’écrire un parser trop fragile.  

⸻

V2 : modèle plus sérieux

Objectif V2

Ajouter une vraie évaluation.

Données :

martj42 historical_results
FIFA historical ranking by country

À ajouter :

backtest.ts
logLoss.ts
calibration.ts
fifaTrendFeatures.ts

Features nouvelles :

rankingTrend1Year
pointsTrend1Year
rankVolatility
pointsVolatility
recentForm

Nouvelle force possible :

strength = 0.7 × normalizedElo + 0.3 × normalizedFifaPoints

Ou :

strength = 0.6 × Elo + 0.2 × FIFA + 0.2 × recentForm

But :

ne plus seulement simuler
mais vérifier si les probabilités sont crédibles

Exemple :

Quand le modèle donne 70 % de victoire,
l’équipe gagne-t-elle environ 70 % du temps ?

⸻

V2.5 : Live Update

Objectif

Permettre au simulateur d’être utilisé pendant la Coupe du Monde.

Flux :

score réel
→ applyRealResult.ts
→ updateEloAfterResult.ts
→ updateFifaRatingAfterResult.ts
→ teamStrength.ts
→ runMonteCarlo.ts

Exemple :

France 2-0 Brésil
→ Elo France augmente
→ Elo Brésil baisse
→ points FIFA France augmentent
→ nouvelle simulation sur les matchs restants

Le simulateur devient dynamique.

⸻

V3 : modèle avancé

Sources nouvelles :

FBref
Transfermarkt
The Odds API
API-Football
Sportradar / Sportmonks si accès API

FBref

But :

xG
xGA
tirs
possession
stats avancées

Utilisation :

expectedGoals.ts
xgFeatures.ts
dixonColesModel.ts

Transfermarkt

But :

effectifs
blessures
âge moyen
valeur équipe
joueurs clés

Utilisation :

playerAvailabilityFeatures.ts
teamStrength.ts

Odds API

But :

comparer notre modèle au marché bookmaker

Exemple :

notre modèle : France gagne 62 %
marché : France gagne 58 %

Utilisation :

compareWithMarket.ts
MarketComparisonTable.tsx

API-Football

But :

fixtures
lineups
injuries
events
live data

API-Football propose justement des données structurées pour fixtures, standings, events, lineups, injuries, odds et predictions.  

⸻

V4 : modèle très avancé

Ajouts possibles :

Dixon-Coles
modèle bayésien
calibration par compétition
xG model
player-level model
market-adjusted probabilities

Dixon-Coles servirait surtout à mieux corriger les petits scores :

0-0
1-0
0-1
1-1

Limite du Poisson indépendant :

les buts des deux équipes sont supposés indépendants

Mais en vrai, un match change selon le score :

une équipe mène 1-0
→ elle défend plus bas
→ la dynamique change

Donc V4 améliore le réalisme, mais ce n’est pas nécessaire pour démarrer.

⸻

Priorité réelle maintenant

Étape 1

Créer et stabiliser :

acquire_data.py

Il doit récupérer :

FIFA Ranking API
FootballRatings Elo
OpenFootball files
martj42 historical results
Elo manuel fallback

Étape 2

Créer :

build_teams.py

Il fusionne :

fifa_rankings_current.json
footballratings_elo.csv
elo_ratings_manual.json
groups.json

en :

teams.json

Étape 3

Créer les parsers OpenFootball :

parse_openfootball_groups.py
parse_openfootball_matches.py
parse_openfootball_bracket.py
parse_openfootball_venues.py

Étape 4

Coder le moteur tournoi :

computeGroupStandings.ts
rankThirdPlacedTeams.ts
buildSlotMap.ts
buildBracket.ts
simulateTournament.ts

Étape 5

Coder le modèle :

teamStrength.ts
expectedGoals.ts
poisson.ts
predictMatch.ts
simulateMatch.ts
runMonteCarlo.ts

⸻

Synthèse finale

Le projet n’est plus seulement :

simulateur visuel Coupe du Monde

Il devient :

plateforme data science de simulation probabiliste

avec :

FIFA = données officielles / points FIFA
FootballRatings = Elo actuel
OpenFootball = structure tournoi exploitable
martj42 = historique pour évaluation
Elo manuel = fallback

La V1 doit rester simple :

Poisson + Elo + FIFA + Monte Carlo

Les versions futures ajoutent progressivement :

évaluation
calibration
live update
features temporelles
xG
blessures
odds
modèles avancés

La meilleure stratégie est donc :

ne pas chercher le modèle parfait maintenant
construire un moteur propre
avoir des données fiables
simuler correctement
évaluer ensuite
améliorer progressivement
