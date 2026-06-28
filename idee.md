
## 1. Incertitude Monte Carlo

Objectif : ne plus afficher seulement `France champion = 17 %`, mais aussi la fiabilité de cette estimation.

À créer :

```text
src/domain/evaluation/monte_carlo_uncertainty.py
```

Ce fichier calcule :

```text
standard_error
ci95_low
ci95_high
coefficient_of_variation
reliability_label
```

À modifier :

```text
src/domain/simulation/run_monte_carlo.py
et tout ce qui est liée
```

Dans `run_monte_carlo.py`, au lieu de sauvegarder seulement :

```json
"champion": 0.17
```

on sauvegarde :

```json
"champion": 0.17,
"champion_se": 0.0038,
"champion_ci95_low": 0.162,
"champion_ci95_high": 0.178,
"champion_cv": 0.022,
"champion_reliability": "high"
```

Dans l’app, on affiche :

```text
France championne : 17.0 %
IC 95 % : [16.2 ; 17.8]
Fiabilité : high
```

Intérêt : ton simulateur devient statistiquement plus sérieux.

> **💡 Explication Mathématique (Incertitude) :**
> La simulation Monte Carlo est une estimation. Si l'on obtient une probabilité $\hat{p}$ (ex: 17%) sur $N$ simulations (ex: 10 000), l'Erreur Standard (SE) se calcule avec la variance de la loi binomiale :
> $SE = \sqrt{\frac{\hat{p}(1 - \hat{p})}{N}}$
> 
> L'Intervalle de Confiance à 95% s'obtient via l'approximation normale (Théorème Central Limite) :
> $IC_{95} = \hat{p} \pm 1.96 \times SE$
> Ainsi, afficher l'IC permet de prouver que la probabilité n'est pas absolue mais encadrée mathématiquement.

---

## 2. Affichage intelligent des événements rares

Objectif : éviter les faux `0.00 %`.

Dans le PDF, le Monte Carlo naïf donne parfois très peu de hits sur des événements rares, ce qui rend l’estimation instable. 

À créer :

```text
src/domain/evaluation/probability_display.py
```

Rôle :

```text
si hits = 0 et n = 10000
afficher < 0.01 %
au lieu de 0.00 %
```

À modifier :

```text
src/domain/simulation/run_monte_carlo.py

app/pages/3_Deltas.py

et tout ce qui est liée
```

Sortie attendue :

```json
{
  "champion": 0.0,
  "champion_hits": 0,
  "champion_display": "< 0.01 %",
  "warning": "No hit observed; event may be rare, not impossible."
}
```

Intérêt : tu montres que tu comprends la différence entre événement impossible et événement non observé.

> **💡 Explication Statistique (La Règle de 3) :**
> En statistiques, lorsqu'un événement ne s'est pas produit sur $N$ essais (0 succès), on ne peut pas dire que la probabilité est de 0. On utilise la "Règle de 3" en biostatistique : la borne supérieure de l'intervalle de confiance à 95% est d'environ $3 / N$. 
> Si $N = 10 000$, la vraie probabilité pourrait être jusqu'à $0.0003$ (soit $0.03\%$). Afficher `< 0.01%` est donc la seule approche scientifiquement rigoureuse.

---

## 3. Étude de convergence Monte Carlo

Objectif : savoir combien de simulations sont nécessaires.

À créer :

```text
src/domain/evaluation/monte_carlo_convergence.py
app/pages/7_MC_Stability.py
outputs/evaluation/mc_convergence.json
```

Principe :

```text
lancer Monte Carlo avec :
100
500
1000
5000
10000
50000 simulations
```

Puis suivre :

```text
P(champion)
P(finale)
P(qualification)
```

pour quelques équipes clés.

À modifier :

```text
src/domain/simulation/run_monte_carlo.py
```

Il faut permettre d’appeler `run_monte_carlo()` proprement depuis un script externe.

Graphiques dans l’app :

```text
x = nombre de simulations
y = probabilité champion
```

Intérêt : tu peux justifier pourquoi tu utilises 10 000 ou 50 000 simulations.

---

## 4. Benchmark coût vs précision

Objectif : comparer les modèles avec leur performance et leur coût.

À créer :

```text
src/domain/evaluation/runtime_benchmark.py
outputs/evaluation/runtime_benchmark.json
app/pages/9_Runtime_Benchmark.py
```

Ce fichier mesure :

```text
modelVersion
nSimulations
runtimeSeconds
meanChampionCV
meanLogLoss
meanBrierScore
```

À modifier :

```text
src/domain/evaluation/model_comparison.py
src/pipeline/run_pipeline.py
```

Sortie attendue :

| Modèle | Simulations | Temps | Log Loss | Brier | CV moyen |
| ------ | ----------: | ----: | -------: | ----: | -------: |
| V1     |      10 000 |  35 s |     0.98 |  0.21 |     0.04 |
| V1.5   |      10 000 |  38 s |     0.96 |  0.20 |     0.04 |
| V2     |      10 000 |  42 s |     0.95 |  0.19 |     0.05 |

Intérêt : tu peux dire si une amélioration vaut vraiment son coût.

---

## 5. Scenario Mode

Objectif : tester des hypothèses.

Exemples :

```text
France -100 Elo
Maroc +100 Elo
Brésil +50 Elo
Espagne -80 Elo
```

À créer :

```text
src/domain/scenario/scenario_config.py
src/domain/scenario/apply_scenario.py
src/domain/scenario/run_scenario.py
app/pages/8_Scenario_Mode.py
outputs/scenarios/
```

À modifier :

```text
src/domain/simulation/simulate_tournament.py
src/domain/simulation/run_monte_carlo.py
```

Concrètement, avant simulation, on applique :

```json
{
  "teamId": "mar",
  "eloDelta": 100
}
```

Puis on compare :

```text
snapshot_baseline
vs
snapshot_scenario_mar_plus_100
```

avec ton Delta Tracker.

Intérêt : tu passes d’un simulateur passif à un outil d’analyse stratégique.

---

## 6. Rare Event Analysis

Objectif : analyser les événements très rares.

Exemples :

```text
Haïti champion
Curaçao en quart
une équipe africaine championne
3 équipes africaines en demi
outsider hors top 50 en finale
```

À créer :

```text
src/domain/rare_events/event_definitions.py
src/domain/rare_events/rare_event_monte_carlo.py
src/domain/rare_events/rare_event_report.py
app/pages/11_Rare_Events.py
outputs/rare_events/
```

À modifier :

```text
src/domain/simulation/simulate_tournament.py
```

Pourquoi ? Il faut que `simulate_tournament()` retourne assez d’informations pour vérifier des événements complexes :

```text
classements
bracket
stade atteint par équipe
confédération
fifaRank
```

Première version simple :

```text
Monte Carlo massif + hits + IC + CV
```

Version avancée plus tard :

```text
importance sampling
splitting
last particle
```

Le PDF montre justement que les événements rares nécessitent des méthodes plus fines que Monte Carlo naïf. 

> **💡 Explication Statistique (Importance Sampling) :**
> L'échantillonnage préférentiel (*Importance Sampling*) est une technique de réduction de la variance. Au lieu de simuler le tournoi normalement et d'attendre qu'Haïti gagne (ce qui n'arrive presque jamais), on *force* mathématiquement Haïti à avoir de bonnes probabilités, puis on corrige le résultat final par le "ratio de vraisemblance" (Likelihood Ratio) pour dé-biaiser le calcul. Cela permet d'estimer des probabilités de l'ordre de $10^{-6}$ avec peu de simulations.

---

## 7. Bradley-Terry/MM rating maison

Objectif : créer ton propre rating statistique à partir des matchs historiques.

C’est probablement l’amélioration scientifique la plus forte.

À créer :

```text
src/domain/rating/bradley_terry_mm.py
src/domain/rating/build_bt_ratings.py
src/domain/rating/rating_utils.py
outputs/ratings/bt_ratings.json
```

À modifier :

```text
src/data/processed/matches_clean.csv
src/domain/prediction/team_strength.py
src/domain/evaluation/model_registry.py
src/domain/evaluation/model_comparison.py
```

Nouveau modèle possible :

```text
V4 = Bradley-Terry + Poisson
```

Pipeline :

```text
matches_clean.csv
↓
filtrer matchs récents
↓
construire matrice victoires/défaites
↓
algorithme MM
↓
rating BT
↓
normalisation
↓
simulation Monte Carlo
```

Lien avec le PDF : le rapport passe d’une force ad hoc à une estimation MM Bradley-Terry, ce qui rend les forces plus défendables statistiquement. 

> **💡 Explication Algorithmique (Bradley-Terry et Algorithme MM) :**
> Le modèle de Bradley-Terry (BT) postule que la probabilité que l'équipe $i$ batte l'équipe $j$ est $P(i > j) = \frac{\lambda_i}{\lambda_i + \lambda_j}$, où $\lambda$ est la "force" latente.
> Pour trouver ces forces $\lambda$ à partir de l'historique, on utilise l'algorithme d'optimisation **MM (Minorization-Maximization)** (équivalent à l'algorithme de Zermelo). C'est un processus itératif extrêmement stable qui maximise la vraisemblance (Maximum Likelihood Estimation) des résultats observés. 
> Pour le football, on utilise l'extension de **Davidson** pour intégrer la probabilité des matchs nuls et un paramètre $\gamma$ pour l'avantage à domicile.

---

## 8. Comparaison Elo / FIFA / Bradley-Terry

Objectif : comprendre les écarts entre sources de force.

À créer :

```text
src/domain/evaluation/rating_comparison.py
app/pages/10_Rating_Comparison.py
outputs/evaluation/rating_comparison.json
```

À modifier :

```text
src/domain/prediction/team_strength.py
src/data/normalized/teams.json
```

Sortie attendue :

```json
{
  "teamId": "fra",
  "eloRank": 3,
  "fifaRank": 1,
  "btRank": 2,
  "rankGapEloFifa": 2,
  "rankGapBtFifa": 1
}
```

Graphiques utiles :

```text
Elo vs FIFA
BT vs FIFA
Elo vs BT
écarts de rang
```

Intérêt : tu expliques pourquoi certains modèles favorisent plus une équipe qu’une autre.

---

## 9. Poisson régressif

Objectif : apprendre directement les lambdas depuis les données.

À créer :

```text
src/domain/models/poisson_regression.py
src/domain/models/train_poisson_regression.py
src/domain/models/predict_lambdas_regression.py
outputs/models/poisson_regression.pkl
outputs/evaluation/poisson_regression_backtest.json
```

À modifier :

```text
src/domain/simulation/simulate_match.py
src/domain/simulation/poisson_model.py
src/domain/evaluation/model_registry.py
```

Aujourd’hui :

```text
lambda_A = baseGoals * exp(diff / scale)
```

Demain :

```text
log(lambda_A) =
beta0
+ beta1 * elo_diff
+ beta2 * fifa_diff
+ beta3 * home_advantage
+ beta4 * recent_form
```

Intérêt : le modèle apprend les buts attendus au lieu d’utiliser une formule imposée.

---

## 10. Dixon-Coles

Objectif : améliorer les petits scores et les nuls.

À créer :

```text
src/domain/models/dixon_coles.py
src/domain/models/train_dixon_coles.py
src/domain/models/dixon_coles_correction.py
outputs/models/dixon_coles_params.json
```

À modifier :

```text
src/domain/simulation/poisson_model.py
src/domain/simulation/simulate_match.py
src/domain/evaluation/model_registry.py
```

Pourquoi ? Le Poisson indépendant sous-estime souvent les corrélations sur les petits scores :

```text
0-0
1-0
0-1
1-1
```

Dixon-Coles ajoute une correction sur ces scores.

Intérêt : meilleur modèle football, surtout pour les nuls.

> **💡 Explication Mathématique (La fonction $\tau$ de Dixon-Coles) :**
> La loi de Poisson de base suppose que les buts de l'équipe A et B sont *indépendants*. Or, le football est un sport à faible score où les équipes s'observent (le 0-0 ou 1-1 sont sur-représentés par rapport au modèle théorique).
> Dixon et Coles ont introduit un paramètre de corrélation $\rho$ et une fonction d'ajustement $\tau(x, y)$.
> Par exemple, pour un 0-0, la probabilité conjointe devient : 
> $P(0, 0) = P_{poisson}(0) \times P_{poisson}(0) \times (1 - \mu_A \mu_B \rho)$
> Cet ajustement subtil corrige le défaut structurel de la loi de Poisson et rend la prédiction des scores exacts redoutablement précise.

---

## 11. Ensemble de modèles

Objectif : combiner plusieurs modèles.

À créer :

```text
src/domain/models/ensemble_model.py
src/domain/models/ensemble_weights.py
src/domain/evaluation/optimize_ensemble_weights.py
outputs/models/ensemble_weights.json
```

À modifier :

```text
src/domain/evaluation/model_registry.py
src/domain/simulation/simulate_match.py
src/domain/prediction/team_strength.py
```

Exemple :

```text
40 % Elo-Poisson
30 % FIFA/Elo hybride
30 % Bradley-Terry
```

Ou pondération apprise :

```text
poids optimisés pour minimiser Log Loss
```

Intérêt : souvent plus robuste qu’un modèle unique.

---

# Ordre recommandé

## Court terme

```text
1. Incertitude Monte Carlo
2. Affichage intelligent des 0 %
3. Convergence Monte Carlo
4. Benchmark coût/précision
```

Ce sont les ajouts les plus faciles et les plus valorisants rapidement.

## Moyen terme

```text
5. Scenario Mode
6. Rare Event Analysis simple
7. Comparaison Elo/FIFA/BT
```

## Long terme

```text
8. Bradley-Terry/MM maison
9. Poisson régressif
10. Dixon-Coles
11. Ensemble de modèles
```

## Fichiers existants les plus concernés

```text
src/domain/simulation/run_monte_carlo.py
src/domain/simulation/simulate_tournament.py
src/domain/simulation/simulate_match.py
src/domain/simulation/poisson_model.py
src/domain/prediction/team_strength.py
src/domain/evaluation/model_registry.py
src/pipeline/run_pipeline.py
app/streamlit_app.py
app/pages/
```

## Conclusion stricte

Le meilleur cap immédiatement n’est pas d’ajouter Dixon-Coles ou Importance Sampling.

Le meilleur cap maintenant est :

```text
probabilités
+ incertitude
+ convergence
+ rare events basiques
+ benchmark coût/précision
```

Puis seulement ensuite :

```text
rating maison Bradley-Terry
+ modèles avancés
```

C’est cette progression qui rendra ton projet propre, défendable et très intéressant dans un portfolio data science.

---

## 12. Amélioration de l'Existant (Ce que nous avons déjà construit)

Objectif : Consolider, optimiser et sublimer les fonctionnalités déjà présentes sur la plateforme avant d'ajouter de nouveaux modèles complexes.

### A. Performance : Parallélisation du Moteur Monte Carlo
- **Constat actuel :** La boucle de 10 000 itérations dans `run_monte_carlo.py` s'exécute de manière synchrone sur un seul cœur du processeur.
- **Amélioration :** Utiliser le module `multiprocessing` ou `concurrent.futures` de Python pour diviser le travail (ex: 4 cœurs calculent 2 500 simulations chacun).
- **Gain :** Le temps de génération du Bracket et des statistiques (actuellement quelques secondes) passera sous la seconde, offrant une expérience vraiment "Live".

### B. UI/UX : Historique Temporel des Deltas (Time-Series)
- **Constat actuel :** L'onglet "Deltas" compare la probabilité *actuelle* avec la probabilité de *début de tournoi*. L'onglet "Bourse Elo" montre la progression globale.
- **Amélioration :** Créer un graphique linéaire (Line Chart) dans l'onglet équipe (`TeamDetail.tsx`) qui retrace la courbe de probabilité de victoire après **chaque** match joué.
- **Gain :** Visualiser la courbe de "hype" d'une équipe, façon graphique boursier historique.

### C. Le mode "God Mode" (Évolution du What-If)
- **Constat actuel :** L'outil "What-If" permet de forcer le score d'un match précis et de voir l'impact sur le classement du groupe.
- **Amélioration :** Permettre de modifier manuellement la force d'une équipe (ex: "+50 Elo" pour la France si Mbappé se blesse) ou d'injecter des résultats pour les matchs à élimination directe, puis de relancer l'Arbre du tournoi.
- **Gain :** Le simulateur devient un outil de "Sandboxing" complet pour tester n'importe quelle théorie farfelue.

### D. Refactoring : Mise en cache du Live Elo
- **Constat actuel :** À chaque simulation, `compute_live_elos` recalcule l'histoire du tournoi depuis le début.
- **Amélioration :** Sauvegarder l'état "Live" de `teams_dict` dans un fichier JSON mis en cache (`teams_live.json`) pour ne recalculer l'Elo que lorsqu'un *nouveau* résultat est posté.
- **Gain :** Économie de ressources serveur et architecture logicielle plus propre.


--------------------------------
Mettre en place ce système de cache (teams_live.json) pour optimiser le serveur ?
Ou attaquer l'évaluation formelle des modèles (Brier Score / LogLoss) pour votre livre blanc ?