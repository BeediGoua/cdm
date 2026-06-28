# World Cup 2026 — next steps

## Objectif du projet

Construire un simulateur de Coupe du Monde 2026 capable de :
- charger et normaliser les données officielles FIFA et les ratings Elo,
- produire une prédiction de scores basée sur un modèle Elo-Poisson,
- exécuter des simulations Monte Carlo sur les matchs restants,
- intégrer les résultats réels en live et recalculer l’état du tournoi.
- challenger les quatre versions de modèle proposées et mesurer si chaque ajout est discriminant.
- comparer la valeur prédictive de chaque étape, du modèle Elo pur au live FIFA dynamique.

## Théorie et modèles utilisés

- Ce projet repose sur un socle mathématique clair : Elo pour la force des équipes, Poisson pour la distribution des buts, et Monte Carlo pour l’incertitude globale.
- L’objectif est de documenter les formules, de garder un modèle simple et interprétable, puis de challenger chaque amélioration proposée.
- Cette section explique pourquoi chaque composant est choisi, quel rôle il joue dans la simulation, et comment il aide à discriminer les quatre versions de modèle.

- Elo : mesure la force relative d’une équipe et fournit une probabilité de victoire.
  - formule principale : `P(A gagne) = 1 / (1 + 10^{-(R_A - R_B) / 400})`.
  - rôle : transforme l’écart de rating entre deux équipes en une probabilité d’issue attendue.
  - pourquoi : un simple classement ne donne pas de différence numérique claire entre deux équipes, tandis qu’Elo donne un score continu.
  - avantage : permet de quantifier l’écart de performance, de supporter des comparaisons transversales, et d’alimenter un modèle statistique.
  - précision : si l’écart est de +100 points, A a environ 64 % de chances de gagner ; si l’écart est de +200, A a environ 76 % de chances.

- Poisson : génère la distribution des buts attendus pour chaque équipe.
  - formule : `P(X = k) = exp(-λ) * λ^k / k!`, avec `k` le nombre de buts et `λ` le taux attendu.
  - rôle : modélise la probabilité que chaque équipe marque 0, 1, 2, ... buts.
  - pourquoi : en football, les comptes de buts sont des événements discrets et rares, ce qui correspond bien à une loi de Poisson.
  - avantage : produit des probabilités de score complètes, ce qui permet d’estimer non seulement victoire/nul/défaite, mais aussi des scores précis.
  - nuance : la modélisation suppose une indépendance approximative entre les buts des deux équipes ; dans sa version simple, elle ne capture pas toutes les corrélations, mais elle reste robuste pour un simulateur de base.
  - précision : cette approximation concerne spécifiquement le modèle de score. Les autres améliorations du modèle (hybride Elo/FIFA, tendances historiques, live FIFA) améliorent la calibration de la force, mais ne corrigent pas directement l’hypothèse d’indépendance des scores.
  - implication : si l’on veut corriger ces corrélations, il faut étudier séparément un modèle bivarié ou un ajustement de type Dixon-Coles / copula.
  - note : dans le cadre de ce projet, la priorité est d’abord de valider le socle Elo-Poisson, puis d’évaluer si un modèle plus complexe apporte un gain discriminant.
- MVP (baseline) : utilise uniquement Elo pour mesurer la force des équipes
  - formule : `strength = Elo` et simulation directe via Elo-Poisson.
  - rôle : établir la version de référence minimale sur laquelle construire les améliorations.
  - avantage : simplicité, interprétabilité totale, pas de dépendances supplémentaires.
  - exemple baseline : France (Elo = 1850) vs Allemagne (Elo = 1820), baseGoals = 1.35, scale = 800.
    - diff = 1850 - 1820 = 30.
    - λ_France = 1.35 × exp(30 / 800) = 1.35 × exp(0.0375) ≈ 1.35 × 1.038 ≈ 1.40.
    - λ_Allemagne = 1.35 × exp(-30 / 800) = 1.35 × exp(-0.0375) ≈ 1.35 × 0.963 ≈ 1.30.
    - P(France gagne) ≈ 0.58 (estimation Elo-Poisson).
    - cette version est le point de comparaison pour V1.5, V2, V3.
- Modèle hybride Elo/FIFA
  - formule : `strength = α × Elo + (1 - α) × FIFA`.
  - rôle : utiliser FIFA Points comme signal de calibration tout en conservant Elo comme base prédictive.
  - pourquoi : quand les valeurs FIFA sont disponibles, elles apportent un second avis sur la force de l’équipe, utile pour réduire les biais de rating.
  - avantage : offre un compromis contrôlé entre deux signaux, avec un coefficient `α` ajustable selon la confiance dans Elo vs FIFA.
  - précision : ce modèle modifie directement l’entrée de la formule Poisson en remplaçant `Elo` par `strength` lors du calcul de l’écart.
  - implication : les lambdas deviennent `λ_A = baseGoals × exp((strength_A - strength_B) / scale)`, ce qui change les distributions de scores et les probabilités de résultat.
  - sortie attendue : probabilités de score et de qualification plus calibrées quand FIFA confirme ou nuance l'Elo.
  - exemple : France (Elo = 1850, FIFA Points = 1765) vs Allemagne (Elo = 1820, FIFA Points = 1764).
    - MVP (Elo pur) : diff = 30, `λ_France ≈ 1.40`, `λ_Allemagne ≈ 1.31`.
    - V1.5 (α = 0.8) : strength_France = 0.8 × 1850 + 0.2 × 1765 = 1830, strength_Allemagne = 0.8 × 1820 + 0.2 × 1764 = 1809, diff = 21, `λ_France ≈ 1.37`, `λ_Allemagne ≈ 1.34`.
    - implication : V1.5 réduit légèrement l'avantage français, car FIFA points confirment une hiérarchie resserrée.
- Tendances historiques FIFA
  - variables : `rankingTrend3Months`, `pointsTrend1Year`, `rankVolatility`.
  - formule possible : `trendScore = w1 × rankingTrend3Months + w2 × pointsTrend1Year - w3 × rankVolatility`.
  - rôle : capturer la dynamique et la stabilité d’une équipe au-delà de son score FIFA statique.
  - pourquoi : une équipe en progression récente mérite un ajustement de force, tandis qu’une équipe volatile peut être moins prévisible.
  - avantage : permet d’enrichir la calibration du modèle en incorporant des signes de forme et de momentum.
  - précision : ce score peut être ajouté à `strength` ou appliqué comme un facteur de pondération lors du calcul des lambdas Poisson.
  - implication : si `trendScore` est positif, la force estimée augmente et la distribution de buts devient plus offensive.
  - sortie attendue : meilleure discrimination des équipes en forme et des équipes en déclin dans les probabilités de match.
  - exemple : Espagne avec rankingTrend3Months = +5 (rang amélioré), pointsTrend1Year = +45, rankVolatility = 2.
    - avec w1 = 0.3, w2 = 0.5, w3 = 0.2 : trendScore = 0.3 × 5 + 0.5 × 45 - 0.2 × 2 = 23.6.
    - force augmente de +23.6, renforçant les lambdas Poisson d'Espagne.
    - Angleterre avec rankingTrend3Months = -8, pointsTrend1Year = -30, rankVolatility = 8 : trendScore = -19.
    - force baisse de -19 malgré un Elo élevé, reflétant un déclin récent.

- Live dynamic FIFA update
  - logique : calculer les nouveaux points FIFA après chaque match réel en suivant la formule du PDF.
  - formule : `Pnew = Pbefore + I × (W - W_e)`.
  - rôle : actualiser le signal FIFA en temps réel, proche de l’update Elo, et refléter l’impact effectif des résultats.
  - pourquoi : cela permet de garder le signal FIFA cohérent avec l’état live du tournoi et de le comparer aux changements d’Elo.
  - avantage : c’est un moyen officiel de mesurer l’évolution de l’équipe dans le temps et d’alimenter un modèle live potentiellement hybride.
  - précision : cette mise à jour FIFA est utile pour le suivi et la validation, mais elle reste un signal complémentaire à Elo dans la simulation de score.
  - implication : `Pnew` alimente la version hybride et peut servir de base à des réajustements de `α` ou des tendances futures.
  - sortie attendue : un état live plus précis avec des forces d'équipe mises à jour et des probabilités qui reflètent la dynamique récente.
  - exemple : Argentine (Pbefore = 1768) vs Canada (Pbefore = 1321).
    - W_e_Argentine = 1 / (1 + 10^{-(1768 - 1321) / 400}) ≈ 0.93.
    - si l'Argentine gagne 2-0, W_Argentine = 1, I = 100 : Pnew_Argentine = 1768 + 100 × (1 - 0.93) = 1775.
    - Canada : W_e_Canada ≈ 0.07, Pnew_Canada = 1321 + 100 × (0 - 0.07) = 1314.
    - implication : après le match, l'état live reflète les points FIFA actualisés : Argentine +7, Canada -7.
- Elo-Poisson : combine l’écart Elo avec une formule de buts attendus pour simuler des scores.
  - formule typique :
    - `diff = Elo_A - Elo_B`
    - `λ_A = baseGoals × exp(diff / scale)`
    - `λ_B = baseGoals × exp(-diff / scale)`
  - rôle : convertit la force relative en un nombre moyen de buts attendus par équipe.
  - pourquoi : l’écart Elo crée une différence de potentiel offensif entre les équipes, et Poisson utilise ce potentiel pour générer des scores.
  - avantage : produit des scores plausibles en gardant un modèle mathématique simple et facile à calibrer.
  - paramètres : `baseGoals` fixe un niveau moyen de buts dans le tournoi, `scale` contrôle la sensibilité de l’écart Elo.
  - exemple : si `baseGoals = 1.35` et `scale = 800`, un écart de 200 points donne `λ_A ≈ 2.24` et `λ_B ≈ 0.81`.

- Monte Carlo : répète les simulations de tournoi pour estimer les probabilités de qualification et de victoire.
  - principe : exécuter `N` simulations indépendantes du tournoi, à chaque fois en générant des scores, des classements et un bracket final.
  - pourquoi : un seul scénario ne capture pas l’incertitude des matchs ; la Monte Carlo transforme la variabilité des scores en probabilités.
  - avantage : fournit des probabilités robustes pour chaque équipe sur des événements incertains, y compris les parcours jusqu’au titre.
  - sortie : par exemple, si une équipe remporte 1 800 tournois sur 10 000 simulations, sa probabilité de victoire est 18 %.
  - précision : l’erreur statistique diminue avec `N`, approximativement `1 / sqrt(N)`.
## Synthèse des discriminants entre les quatre versions

Pour valider que chaque version apporte une amélioration mesurable, nous comparons les probabilités de résultat et de qualification pour le même match :

- **Discriminant 1 (MVP vs V1.5)** : avec le modèle hybride, les équipes proches en Elo mais différentes en FIFA Points produisent des lambdas réajustées.
  - exemple France-Allemagne : MVP donne P(France) ≈ 0.58, V1.5 avec α = 0.8 donne P(France) ≈ 0.55 (plus serré).
  - quand FIFA Points confirme un écart Elo, V1.5 amplifie ; quand FIFA modère, V1.5 réduit.
  - validation : comparer les distributions de scores simulées sur 10 000 matchs ; mesurer si V1.5 produit des scores plus calibrés.

- **Discriminant 2 (V1.5 vs V2)** : les tendances historiques enrichissent les équipes en forme et pénalisent les équipes en déclin.
  - exemple Espagne vs Angleterre : Espagne en progression (+23.6 trend) devient plus forte que l'Elo seul, Angleterre en déclin (-19 trend) devient plus faible.
  - V1.5 ignore ces tendances, V2 les capture explicitement dans le calcul de lambda.
  - validation : mesurer si V2 prédit mieux les résultats des équipes en phase ascendante ou descendante ; calculer l'écart absolu entre prédiction et résultat réel.

- **Discriminant 3 (V2 vs V3)** : la mise à jour dynamique FIFA reflète l'évolution live du tournoi.
  - exemple Argentine après victoire : Pbefore = 1768, Pnew = 1775 (+7 points).
  - V2 conserve des points figés au démarrage du tournoi, V3 les actualise après chaque match réel.
  - V3 génère des prédictions plus récentes et plus alignées avec la dynamique observée.
  - validation : durant le tournoi, vérifier si V3 produit des probabilités de qualification plus proches du taux de victoire observé après quelques matchs.

- **Résumé des outputs attendus** :
  - MVP : P(France vs Allemagne) ≈ 0.58 victoire, distribution moyenne.
  - V1.5 : P(France vs Allemagne) ≈ 0.55 victoire, distribution plus serrée et calibrée.
  - V2 : P(Espagne vs Angleterre) très différent de MVP si tendances marquées ; discrimination fine des équipes.
  - V3 : P(victoire après jour 2) converge vers le taux observé après jour 2 si modèle cohérent.
## Comment on va utiliser ces modèles

### FIFA API vs PDF FIFA
- l’API FIFA fournit le ranking et les points actuels : c’est le résultat du calcul.
- le PDF FIFA explique le mécanisme de mise à jour des points après match.
- distinction clé : l’API est le signal observé, le PDF est la règle de transformation.
- on ne remplace pas Elo par la formule FIFA ; on conserve Elo comme base prédictive et on utilise FIFA comme calibration, validation ou signal complémentaire.

- `teams.json` fournira les forces des équipes :
  - `elo` pour mesurer la force relative via le modèle Elo.
  - `fifaRank` et `fifaPoints` comme variables complémentaires pour la calibration et la qualité du rating.
  - `fifaPoints` peuvent aussi alimenter une version hybride de la force, par exemple `0.8 × Elo + 0.2 × FIFA Points`.
  - `sourceConfidence` pour savoir si l’Elo vient d’une source primaire, secondaire ou d’un Elo manuel.
  - pourquoi : le modèle Elo utilise directement `elo` pour calculer `P(A gagne)` et pour comparer deux équipes dans `poisson_model.py`.
  - précision : comme `elo` est renseigné manuellement puis mis à jour par la formule Elo, il doit rester la variable principale de simulation.
  - clarification : `fifaPoints` et `fifaRank` servent plutôt à vérifier, calibrer ou corriger le modèle, mais ne doivent pas remplacer `elo` dans la simulation de base.
  - meilleure pratique : garder `elo` comme noyau prédictif, utiliser `fifaPoints` pour détecter un biais ou ajuster `scale`/`baseGoals`, et utiliser `fifaRank` comme indice ordinal de confiance.

- `groupMatches.json` définira les matchs à simuler et les `matchday` à prendre en compte :
  - `homeTeamId`, `awayTeamId`, `group`, `date`, `venueId`, `matchday`.
  - pourquoi : ces éléments identifient chaque rencontre, permettent de distinguer les matchs joués des matchs restants, et servent de base à la construction du bracket.
  - lien théorie : la structure du tournoi (groupes + journées) est nécessaire pour appliquer ensuite les formules de classement et les simulations Monte Carlo.

- `real_results.json` alimentera le moteur live pour figer les matchs joués et mettre à jour les classements :
  - `matchId`, `homeTeamId`, `awayTeamId`, `homeGoals`, `awayGoals`, `status`, `source`, `updatedAt`.
  - pourquoi : ces données réelles servent de vérité de terrain et empêchent la resimulation d’un match déjà joué.
  - lien théorie : les résultats réels provoquent des mises à jour Elo/FIFA dans `points_update.py` et modifient les entrées de Monte Carlo.

- `poisson_model.py` convertira les écarts Elo en `lambda` de buts :
  - prendra `eloA`, `eloB` et appliquera `λ = baseGoals × exp(diff / scale)`.
  - pourquoi : cette conversion relie la théorie Elo à la loi de Poisson, transformant une force relative en attentes de buts.
  - résultat : deux taux `λ_home`, `λ_away` utilisés pour générer des scores plausibles.

- `simulate_match.py` produira un score simulé pour chaque rencontre :
  - utilisera `poisson.pmf` ou un tirage Poisson à partir de `λ_home` et `λ_away`.
  - pourquoi : il transforme les probabilités de buts en un score concrètement jouable.
  - lien théorie : cette étape applique la distribution Poisson pour chaque équipe, puis convertit les scores en résultat match (victoire/nul/défaite).

- `simulate_tournament.py` et `run_monte_carlo.py` calculeront des probabilités sur des milliers de scénarios :
  - `simulate_tournament.py` exécute une simulation complète du tournoi à partir de l’état live et des matchs restants.
  - `run_monte_carlo.py` répète cette simulation `N` fois, agrège les résultats et calcule les probabilités.
  - pourquoi : la théorie Monte Carlo est nécessaire pour passer de scénarios individuels à des probabilités stables.
  - sorties : chances de qualification, passage en 8es/quarts/demis/finale, titres, et distribution des scores.

## Sorties attendues

- classement de groupe recalculé en live,
- état du tournoi : matchs joués, matchs restants, qualifiés,
- probabilités de passage en 8es, quarts, demies, finale et victoire,
- distribution des scores et probabilités de résultat pour chaque match,
- fichiers de données enrichis pour analyses et tests.

## Ce qui est déjà réalisé

- normalisation des équipes et des données FIFA dans `src/data/normalized/`
- priorisation des sources Elo :
  - `world_football_elo.csv` (source primaire)
  - `footballratings_elo.csv` (source secondaire)
  - `footballratings_elo_fallback.csv` (fallback FIFA)
- support des Elo manuels via `src/data/raw/elo_ratings_manual.json`
- résolution d’alias et correspondance d’ID pour appliquer les Elo aux bonnes équipes
- champs tracés dans `teams.json` : `elo`, `eloSource`, `sourceConfidence`
- pipeline d’acquisition/validation/normalisation via `src/data_acquisition/main.py`

## Ce qui manque encore

- aucune logique de live update du tournoi avec résultats réels
- pas de moteur Monte Carlo dans le dépôt Python actuel
- pas d’implémentation Elo-Poisson / simulation de score
- pas de gestion des matchs déjà joués ni de relance de simulation sur les matchs restants
- pas de fichier central de résultats réels (live) dans `src/data/raw/`

## Vision du projet

Le simulateur doit être un outil sérieux et réaliste, basé sur :
- les règles officielles FIFA pour le format 2026
- des données FIFA et OpenFootball fiables
- des ratings Elo pour la force des équipes
- un modèle Elo-Poisson pour la prédiction des scores
- une simulation Monte Carlo pour estimer probabilités et issues
- un moteur live capable de prendre en compte les scores réels au fil de l’eau

## Roadmap modèle

- MVP : `strength(team) = elo(team)` et simulation basée sur Elo-Poisson + Monte Carlo.
- V1.5 : intégrer `fifaPoints` comme signal complémentaire, par exemple `strength = 0.8 × Elo + 0.2 × FIFA Points`.
- V2 : ajouter des features historiques FIFA (`rankingTrend3Months`, `pointsTrend1Year`, `rankVolatility`) pour enrichir la calibration.
- V3 : mettre en place la mise à jour dynamique des points FIFA en live via le PDF officiel, avec `updateFifaRatingAfterResult.py`.

## Sources de données à utiliser

### Sources principales

- FIFA : groupes, calendrier, stades, règles de qualification, règles de départage
- World Football Elo Ratings / FootballRatings : force des équipes
- OpenFootball 2026 : structure libre des Coupes du Monde, calendrier, stades, playoffs
- Kaggle / martj42 international_results : résultats historiques pour backtesting et calibration
- PDF récupérés : logique UX, bracket, barragistes, départages (pas source de vérité)

### Fichiers bruts recommandés

- `src/data/raw/fifa_rankings_current.json`
- `src/data/raw/footballratings_elo.csv`
- `src/data/raw/openfootball_cup.txt`
- `src/data/raw/openfootball_cup_finals.txt`
- `src/data/raw/openfootball_stadiums.csv`
- `src/data/raw/openfootball_quali_playoffs.txt`
- `src/data/raw/historical_results.csv`
- `src/data/raw/elo_ratings_manual.json`
- `src/data/raw/real_results.json`

### Fichiers normalisés cibles

- `src/data/normalized/teams.json`
- `src/data/normalized/groups.json`
- `src/data/normalized/groupMatches.json`
- `src/data/normalized/venues.json`
- `src/data/normalized/bracketRules.json`
- `src/data/normalized/playoffs.json`

### Fichier de traitement

- `src/data/processed/matches_clean.csv`

## Données normalisées attendues

### `teams.json`

Doit contenir :
- `id`, `fifaCode`, `nameFr`, `nameEn`
- `group`, `confederation`, `flagCode`
- `fifaRank`, `fifaPoints`
- `elo`, `eloRank`, `eloSource`, `eloDate`
- `sourceConfidence`

Cet objet est la base de force des équipes, en combinant :
- FIFA Ranking
- FootballRatings Elo
- Elo manuel fallback
- groupement et confédération

### `groups.json`

Représente la composition des 12 groupes.
Exemple :

```json
{
  "A": ["mex", "rsa", "kor", "playoff_uefa_d"],
  "B": ["can", "playoff_uefa_a", "qat", "sui"]
}
```

### `groupMatches.json`

Doit contenir :
- `id`, `group`, `homeTeamId`, `awayTeamId`
- `date`, `timeLocal`, `venueId`, `matchday`

`matchday` est essentiel pour le live update :
- journée 1
- journée 2
- journée 3
- phase finale

### `bracketRules.json`

Fichier critique pour :
- phase finale à 32 équipes
- 8 meilleurs troisièmes
- propagation des vainqueurs

Ce fichier doit être testé rigoureusement.

### `real_results.json`

Doit contenir les scores réels :
- `matchId`, `homeTeamId`, `awayTeamId`
- `homeGoals`, `awayGoals`
- `status` (`played`, `postponed`, `cancelled`)
- `source`, `updatedAt`

Ce fichier est la source de vérité pour le live update.

## Architecture cible

### Structure recommandée

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

### Dossiers prioritaires

- `src/domain/live/` : logique de résultats réels, gel des matchs, classement, état du tournoi
- `src/domain/simulation/` : modèle Elo-Poisson et Monte Carlo
- `src/data/raw/` : fichier de scores réels et Elo manuels
- `src/data/normalized/` : fichiers source du simulateur
- `tests/` : validation des règles et de la simulation

### À ne pas ajouter maintenant

- monitoring/
- supabase/
- charts/
- venue-map/
- advanced-models/

Ces éléments sont utiles plus tard, mais la priorité est le moteur live + simulation.

## Live update : conception

### Composants live

- `src/domain/live/load_real_results.py`
  - lecture et validation de `real_results.json`
  - mapping des scores vers les matchs normalisés

- `src/domain/live/freeze_matches.py`
  - marque les matchs joués
  - empêche leur resimulation
  - gère les statuts `played`, `postponed`, `cancelled`

- `src/domain/live/group_standings.py`
  - calcule les classements de groupe sur la base des résultats réels
  - applique : points, différence de buts, buts marqués, fair-play si besoin

- `src/domain/live/points_update.py`
  - met à jour les points Elo après chaque résultat réel
  - applique des snapshots journaliers ou des formules d’update

- `src/domain/live/updateFifaRatingAfterResult.py`
  - met à jour les points FIFA selon la formule PDF FIFA
  - calcule `Pnew = Pbefore + I × (W - W_e)` et stocke `updatedFifaPoints`

- `src/domain/live/live_state.py`
  - regroupe l’état courant du tournoi : matchs joués, matchs restants, classements, équipes
  - définit les entrées pour le moteur de simulation

### Comportements attendus

- ajout manuel d’un score → `played=true`
- matchs terminés exclus des relances de simulation
- classement de groupe recalculé immédiatement
- recalcul des points Elo/FIFA possible automatiquement ou via import manuel
- support de matchs annulés / reportés et des 8 meilleurs troisièmes

### Cas d’usage

- avant tournoi : aucun résultat, puis simulation complète pré-tournoi
- pendant tournoi : résultats journaliers ajoutés, matchs joués fixés, simulations sur la suite
- post-tournoi : collecte des résultats et évaluation du modèle
- si un nouveau fichier FIFA arrive : import et mise à jour de l’état

## Simulation : conception

### Dossier `src/domain/simulation/`

- `poisson_model.py` : convertir l’écart Elo en buts attendus
- `simulate_match.py` : générer un score simulé entre deux équipes
- `simulate_tournament.py` : simuler les matchs restants et le bracket
- `run_monte_carlo.py` : exécuter des simulations en boucle et calculer probabilités

### Entrées attendues

- équipes normalisées (Elo, FIFA, confédération)
- groupes et calendrier
- matchs joués / restants
- résultats réels présents dans `real_results.json`

### Flux d’une simulation

1. charger l’état live et les matchs restants
2. calculer les probabilités score pour chaque match
3. simuler les scores avec des lois de Poisson
4. déduire victoire/nul/défaite
5. propager le bracket pour chaque simulation
6. agréger les résultats sur N simulations

### Résultats attendus

- probabilités de qualification
- probabilités de passage en 8es / quarts / demies / finale
- probabilité de champion
- distribution de scores

## Théorie à inclure

### Elo

- `P(A gagne) = 1 / (1 + 10^{-(R_A - R_B)/400})`
- sert à mesurer la force relative des équipes
- utilisé pour produire des probabilités de match

### Elo après résultat

- `R_n = R_o + K × G × (W - W_e)`
- `W` = résultat observé
- `W_e` = résultat attendu
- `K` = importance du match
- `G` = multiplicateur de marge

### FIFA Ranking

- API FIFA = résultat du classement et des points actuels.
- PDF FIFA = mécanisme de calcul/mise à jour des points après match.
- formule proche d’Elo : `P_new = P_before + I × (W - W_e)`
- utile comme variable complémentaire, pas comme remplacement de l’Elo pour la simulation de score.

### Elo-Poisson

- `lambda_A = baseGoals × exp(diff / scale)`
- `lambda_B = baseGoals × exp(-diff / scale)`
- `P(X = k) = exp(-λ) × λ^k / k!`
- les deux scores sont simulés indépendamment

### Classement de groupe

- `points = 3 × victoires + 1 × nuls`
- `goalDifference = goalsFor - goalsAgainst`
- si égalité : différence de buts, buts marqués, fair-play, choix manuel

### Monte Carlo

- `P(champion) = nombre de titres / nombre de simulations`
- erreur approximative : `1 / sqrt(N)`
- utile pour estimer les probabilités globales du tournoi

## Feuille de route détaillée

### Étape 1 — data / normalisation

- valider que `teams.json` contient bien les Elo manuels appliqués
- vérifier que tous les IDs de `groups.json` et `groupMatches.json` existent dans `teams.json`
- vérifier la présence de `matchday` dans `groupMatches.json`
- conserver la traçabilité des sources Elo via `sourceConfidence`
- normaliser les données issues de FIFA, OpenFootball, FootballRatings et historique

### Étape 2 — architecture live + simulation

- définir `src/domain/live/` et `src/domain/simulation/`
- ajouter `src/data/raw/real_results.json`
- créer les modules live et simulation listés ci-dessus
- distinguer clairement :
  - live update = résultats réels + état actuel
  - simulation = matchs restants + probabilités

### Étape 3 — documentation et tests

- documenter le flux dans un `.md` (ce document doit rester central)
- ajouter des tests unitaires pour :
  - application des Elo manuels
  - résolution d’alias et correspondances d’équipe
  - import de résultats réels
  - gel des matchs joués
  - calcul de classement de groupe
  - simulation de score Elo-Poisson
  - exécution Monte Carlo

### Étape 4 — validation de la V1

- vérifier les probabilités des équipes favorites
- contrôler les meilleurs troisièmes et les règles du bracket
- comparer les résultats simulés à un historique ou à un cas réel
- ajuster la formule `baseGoals` / `scale` si nécessaire

## Conclusion

Le prochain livrable est une version V1 sérieuse et réaliste, centrée sur :
- un moteur live capable de gérer les résultats réels
- une simulation basée sur des Elo normalisés et des règles FIFA
- un pipeline de données clair et testable
- un document central unique dans `remarques/WorldCup2026_Next_Steps_Live_Update.md`

Ce document devient la référence du projet. Toutes les décisions de conception doivent s’aligner sur cette feuille de route.

## Plan détaillé et procédure

### 1. Ce qui est déjà prêt

- `src/data_acquisition/main.py` prépare le pipeline d'acquisition, de validation et de normalisation.
- `src/data/normalized/` contient déjà les fichiers de base : `teams.json`, `groups.json`, `groupMatches.json`, `venues.json`, `bracketRules.json`.
- Les Elo manuels sont gérés dans `src/data/raw/elo_ratings_manual.json` et tracés dans `teams.json` via `elo`, `eloSource`, `sourceConfidence`.
- La résolution d'alias et la normalisation des équipes permettent d'appliquer les Elo aux bons `teamId`.

### 2. Données utilisées

- `teams.json` : identifiants d'équipes, nom, Elo actuel, source de l'Elo, `sourceConfidence`, et éventuellement des données FIFA complémentaires.
- `groups.json` : structure des groupes et liste des équipes par groupe.
- `groupMatches.json` : calendrier des matchs de groupes, avec `matchId`, `homeTeamId`, `awayTeamId`, date, stade.
- `venues.json` : stades d'accueil et localisation.
- `bracketRules.json` : règles de qualification et de classement.
- `src/data/raw/real_results.json` : résultats réels entrants, incluant au minimum :
  - `matchId`
  - `homeTeamId`
  - `awayTeamId`
  - `scoreHome`
  - `scoreAway`
  - `played` (bool)
  - `date`
  - `status` éventuel (`played`, `postponed`, `cancelled`)
- `src/data/raw/elo_ratings_manual.json` : Elo manuels ajoutés avant tournoi.

### 3. Procédure de développement

1. Préparation et validation des données
   - exécuter le pipeline d'acquisition pour produire `teams.json`, `groups.json`, `groupMatches.json`.
   - valider que tous les `teamId` dans `groups.json` et `groupMatches.json` existent dans `teams.json`.
   - vérifier que les Elo manuels sont bien appliqués et que `sourceConfidence` conserve la traçabilité.
   - vérifier que `matchday` est présent dans `groupMatches.json` et que les matchs sont correctement identifiés en journée/phase.
   - vérifier la cohérence des données FIFA complémentaires (`fifaPoints`, `fifaRank`) si elles sont présentes.
   - valider la normalisation des équipes, stades et règles de bracket pour le format 2026.

2. Construction du moteur live
   - créer `src/data/raw/real_results.json` comme source officielle de résultats réels.
   - charger ce fichier depuis un module `src/domain/live/load_real_results.py` et valider la forme des données.
   - vérifier que `real_results.json` correspond aux `matchId` normalisés et aux `teamId` attendus dans `groupMatches.json`.
   - marquer les rencontres terminées avec `played=true` dans `src/domain/live/freeze_matches.py`.
   - gérer les statuts `played`, `postponed`, `cancelled` et exclure les matchs non joués de la simulation.
   - recalculer les classements de groupes dans `src/domain/live/group_standings.py`.
   - regrouper l’état courant du tournoi dans `src/domain/live/live_state.py`, puis exposer les matchs joués et les matchs restants.
   - mettre à jour les notations des équipes dans `src/domain/live/points_update.py` après les résultats réels.
   - ajouter `src/domain/live/updateFifaRatingAfterResult.py` pour mettre à jour les points FIFA via le PDF FIFA après chaque match réel.
   - prévoir un mécanisme de recharge des points/rangs FIFA depuis l’API si disponible après mise à jour locale.
   - figer les anciens scores : les matchs joués restent archivés et ne sont jamais resimulés.

3. Construction du moteur de simulation
   - créer `src/domain/simulation/poisson_model.py` pour convertir un écart Elo en lambdas de buts.
   - créer `src/domain/simulation/simulate_match.py` pour produire un score simulé entre deux équipes.
   - créer `src/domain/simulation/simulate_tournament.py` pour simuler les matchs restants et le bracket.
   - créer `src/domain/simulation/run_monte_carlo.py` pour lancer des milliers d’itérations et calculer des probabilités.
   - veiller à ce que le moteur de simulation consomme l’état fourni par `live_state.py` afin de ne simuler que les matchs restants.
   - prévoir une option de force hybride `strength = 0.8 × Elo + 0.2 × FIFA Points` pour les versions évoluées.
   - prévoir le calcul des 8 meilleurs troisièmes et des règles de départage propres au format 2026.
   - définir clairement le point de transition : live update met à jour les forces, simulation génère uniquement l’avenir.

4. Tests et validation
   - tests unitaires pour la bonne application des Elo manuels.
   - tests de validation de l’alias et de la correspondance `teamId`.
   - tests de validation des données `real_results.json` et des statuts de match.
   - tests du flux live : import de résultats, gel des matchs, recalcul de groupes.
   - tests du moteur live FIFA : `updateFifaRatingAfterResult.py`, mise à jour des points FIFA, cohérence `Pnew`.
   - tests du rafraîchissement des points/rangs FIFA via API si possible.
   - tests de simulation : distribution de scores, probabilités victoire/nul/défaite, résultats de Monte Carlo.
   - tests d’intégration live → simulation : vérifier que les matchs joués ne sont pas relancés.
   - tests de cas 2026 : meilleurs troisièmes, reportés/annulations, propagation correcte du bracket.
   - tests d’intégration historique : confirmer que les scores figés restent immuables et que le modèle évolue uniquement sur les matchs futurs.

### 4. Théorie à expliquer

- Elo
  - `P(A gagne) = 1 / (1 + 10^{-(R_A - R_B) / 400})`
  - L'Elo est une force relative d'équipe qui permet d'estimer la probabilité de victoire.
  - c'est un score continu : un écart de 100 points correspond à environ 64 % de chances, 200 points environ 76 %.
  - l'Elo doit être la source principale du modèle de force dans la simulation de base.
  - mise à jour après match : `R_n = R_o + K × G × (W - W_e)`.
    - `W` = résultat observé (1/victoire, 0.5/nul, 0/défaite).
    - `W_e` = probabilité attendue dérivée de l'écart Elo.
    - `K` = importance du match (qualification, phase finale, etc.).
    - `G` = multiplicateur de marge ou multiplicateur selon l'importance du score.
  - rôle : fournir un signal robuste de force pour comparer deux équipes, en particulier lorsque les données FIFA sont incomplètes ou hétérogènes.

- FIFA Ranking / points
  - l'API FIFA donne les points et le rang actuels : c'est un signal observé.
  - le PDF FIFA donne la règle de mise à jour des points : `Pnew = Pbefore + I × (W - W_e)`.
  - utile pour calibration, validation et suivi live, mais pas pour remplacer le calcul de score.
  - dans les versions avancées, `fifaPoints` peuvent enrichir la force : `strength = 0.8 × Elo + 0.2 × FIFA Points`.
  - le classement FIFA est un indicateur ordinal de confiance, pas un modèle de match.

- Poisson
  - on modélise les buts de chaque équipe comme une loi de Poisson indépendante.
  - `P(X = k) = exp(-λ) * λ^k / k!`.
  - `λ_home` et `λ_away` sont dérivés de l'écart Elo et d'un niveau moyen de buts (`baseGoals`, `scale`).
  - formule typique :
    - `diff = Elo_A - Elo_B`
    - `λ_A = baseGoals × exp(diff / scale)`
    - `λ_B = baseGoals × exp(-diff / scale)`
  - cela transforme la force relative en une attente de buts, puis en une distribution de score.
  - nuance : la dépendance entre les deux équipes est approximée, ce qui est acceptable pour une simulation de base mais peut être amélioré plus tard.

- Simulation
  - chaque match simulateur génère un score selon deux lois de Poisson.
  - on interprète ensuite le score pour obtenir le résultat du match (victoire/nul/défaite).
  - Monte Carlo répète ces simulations pour estimer les probabilités d'issues : qualification, passage de tour, champion.
  - les résultats de Monte Carlo fournissent une distribution : `P(champion)`, `P(8es)`, `P(quarts)`.
  - l'erreur statistique diminue avec le nombre de simulations, approximativement `1 / sqrt(N)`.
  - le flux de simulation doit toujours consommer l’état live, c’est-à-dire ne simuler que les matchs restant à jouer.
  - les matchs déjà joués sont figés dans l’historique : leurs scores ne sont pas resimulés, et ils servent de base pour recalculer la force des équipes.
  - après chaque nouvelle vraie rencontre, on met à jour l’Elo des équipes concernées, puis on recharge ou met à jour les points FIFA / rang FIFA si une API est disponible.
  - il faut prévoir dans la procédure que la mise à jour live se déroule ainsi : 
    1. ingérer les scores réels dans `real_results.json` et marquer `played=true`.
    2. recalculer les classements de groupe avec les résultats figés.
    3. mettre à jour l’Elo sur la base des résultats réels.
    4. appliquer la formule PDF FIFA pour actualiser `updatedFifaPoints` et, si possible, recharger les points/rang FIFA depuis l’API.
    5. reconstruire l’état live (`live_state.py`) et relancer la simulation uniquement sur les matchs non joués.
  - en pratique, les anciens scores restent figés et ne sont pas modifiés : ils constituent l’archive historique du tournoi, tandis que le modèle évolue uniquement sur la suite des matchs.
  - le recalcul des forces à partir des résultats réels garantit que la simulation utilise des Elo et FIFA à jour pour les matchs futurs.

- Classement de groupe
  - points = 3 × victoire + 1 × nul + 0 × défaite.
  - `goalDifference = goalsFor - goalsAgainst`.
  - `goalsFor` est la somme des buts marqués.
  - en cas d'égalité : utiliser les départages officiels (différence de buts, buts marqués, éventuellement fair-play, tête-à-tête, tirage au sort). 
  - pour 2026 : prévoir le calcul des 8 meilleurs troisièmes en phase de groupes.
  - le classement doit être recalculé à chaque mise à jour live pour déterminer les qualifiés.

- Version de modèle
  - objectif : challenger les quatre versions proposées et vérifier si chaque couche d’ajout améliore réellement la discrimination des résultats.
    - test : comparer la précision de chaque version sur des scénarios historiques ou des jeux de validation.
    - critère : l’ajout est discriminant s’il améliore les probabilités de qualification, les prédictions de score, ou la cohérence avec les classements observés.
  - MVP : force = `Elo`, simulation Elo-Poisson, Monte Carlo.
    - valeur : simplicité, robustesse et cohérence théorique. L’Elo reste le noyau prédictif et fournit une probabilité directe de victoire.
    - avantage : modèle facile à expliquer, facile à calibrer, et qui évite de mélanger des métriques issues de calculs différents.
    - formule clé : `P(A gagne) = 1 / (1 + 10^{-(R_A - R_B) / 400})`.
  - V1.5 : ajouter `FIFA Points` comme signal complémentaire de force.
    - valeur : permet d’utiliser une information observable supplémentaire pour corriger des biais Elo locaux ou des effets de forme.
    - avantage : meilleure stabilité lorsque l’Elo est incertain ou lorsque les points FIFA confirment la hiérarchie.
    - exemple : `strength = 0.8 × Elo + 0.2 × FIFA Points` ou plus généralement `strength = α × Elo + (1 - α) × FIFA`.
  - V2 : ajouter des variables de tendance historique FIFA (`rankingTrend3Months`, `pointsTrend1Year`, `rankVolatility`).
    - valeur : capter la dynamique récente d’une équipe, pas seulement son niveau absolu.
    - avantage : différencier une équipe en forme d’une équipe qui stagne, et mieux anticiper les fluctuations de performance.
    - formule possible : `trendScore = w1 × rankingTrend3Months + w2 × pointsTrend1Year - w3 × rankVolatility`.
  - V3 : live dynamic FIFA update avec `updateFifaRatingAfterResult.py` et `Pnew = Pbefore + I × (W - W_e)`.
    - valeur : intégrer la logique officielle FIFA de mise à jour des points en temps réel, avec la même forme que l’Elo.
    - avantage : produire un signal FIFA actualisé après chaque match réel, tout en conservant l’Elo comme base de simulation.
    - formule : `Pnew = Pbefore + I × (W - W_e)` où `W` est le résultat observé, `W_e` l’espérance de résultat et `I` l’importance du match.

### 5. Architecture finale des dossiers et fichiers

- `src/domain/live/`
  - `__init__.py`
  - `load_real_results.py`
  - `freeze_matches.py`
  - `group_standings.py`
  - `points_update.py`
  - `live_state.py`
  - `updateFifaRatingAfterResult.py` (existante, à réutiliser / améliorer)
- `src/domain/simulation/`
  - `__init__.py`
  - `poisson_model.py`
  - `simulate_match.py`
  - `simulate_tournament.py`
  - `run_monte_carlo.py`
- `src/data/raw/`
  - `real_results.json`
  - `elo_ratings_manual.json`
- `tests/`
  - `test_live_update_and_simulation.py` ou extension de `tests/test_resolution_and_fifa_update.py`
- `remarques/` ou `README.md`
  - ajouter un document de spécification ou une section explicative du flux live + simulation.

### 6. Mode d’emploi attendu

- étape 1 : exécuter la normalisation des données pour produire les fichiers de référence.
- étape 2 : alimenter `src/data/raw/real_results.json` avec les scores réels.
- étape 3 : exécuter le module live pour mettre à jour le statut des matchs et recalculer les groupes.
- étape 4 : exécuter le moteur de simulation sur les matchs restants pour générer des probabilités.
- étape 5 : comparer les résultats simulés avec les données réelles et ajuster la formule Elo-Poisson si nécessaire.

### 7. Conclusion recommandée

Le prochain livrable doit être un pipeline clair en deux parties :
- un moteur « live » qui tient à jour l’état du tournoi et verrouille les matchs joués ;
- un moteur de simulation Monte Carlo qui utilise les Elo actuels et ne simule que les matchs non joués.

L’objectif est de garder la normalisation initiale intacte, d’ajouter un point d’entrée `real_results.json`, puis de construire un moteur stable qui fonctionne en mode « avant tournoi », « en cours » et « post-tournoi ».
