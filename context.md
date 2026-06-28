# Runbook - Simulateur Coupe du Monde 2026

En supposant que **tout le projet est implémenté**, voici un runbook complet, pas-à-pas, clair du début à la fin. Il inclut les commandes à exécuter, la suppression des caches Python et une option pour produire un snapshot Monte Carlo haute-fidélité.

## Prérequis rapides

- Un environnement virtuel Python activé (ex. `.venv`), Python 3.11.
- Installer les dépendances :

```bash
python -m venv .venv
# PowerShell :
.\.venv\Scripts\Activate.ps1   
# Bash (Linux/Mac) :
# source .venv/bin/activate
pip install -r requirements.txt
```

### Nettoyer caches Python (fortement recommandé après modifications de code)

```powershell
# Depuis la racine du projet, pour PowerShell
Get-ChildItem -Path . -Recurse -Force -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -Force -Filter '*.pyc' | Remove-Item -Force -ErrorAction SilentlyContinue

# Ou spécifiquement pour un module :
Remove-Item -Recurse -Force src\domain\evaluation\__pycache__
```
Après suppression des caches, fermez et rouvrez votre terminal (ou redémarrez l'interpréteur) pour purger sys.modules en mémoire.

---

## Phase A : Préparation avant le début du tournoi

Cette phase n'est faite qu'une seule fois.

### 0) Acquisition des données (téléchargement)

Avant d'exécuter la validation, téléchargez / préparez les sources brutes. Le dossier `src/data_acquisition` contient une pipeline et des utilitaires.

Commande recommandée (pipeline complète) :

```bash
python src/data_acquisition/main.py
```

Options utiles :
- `--no-fetch` : saute le téléchargement des fichiers bruts (utile si vous avez déjà `src/data/raw/`).
- `--no-validate` : saute la validation des fichiers bruts.
- `--no-normalize` : saute la normalisation vers JSON.
- `--no-import` : saute l'import dans SQLite.

Si vous préférez lancer des étapes individuelles :

```bash
# télécharger les sources brutes
python src/data_acquisition/fetch_data.py

# récupérer les Elo (eloratings / fallback)
python src/data_acquisition/fetch_world_elo.py

# normaliser
python src/data_acquisition/normalize_data.py

# importer dans SQLite
python src/data_acquisition/import_sqlite.py
```

Courte analyse des dossiers liés aux données :
- `src/data/raw/` : fichiers sources bruts téléchargés (CSV, JSON, OpenFootball, etc.)
- `src/data/normalized/` : fichiers JSON nettoyés et normalisés pour le simulateur
- `src/data/processed/` : données finales prêtes à l'usage (matches_clean.csv, etc.)

Vérifiez `src/data/raw/` après l'étape d'acquisition avant d'appeler la validation.

### 1) Valider les données

```bash
python scripts/validate_data.py
```

Vérifie : `teams.json`, `groups.json`, `groupMatches.json`, `venues.json`, `bracketRules.json`.
Résultat attendu :
```text
Validation OK.
0 erreur détectée.
```

### 2) Calibration du modèle V1

Cette étape permet de calculer les valeurs optimales pour les buts de base et le scale. Ces paramètres deviennent les paramètres officiels.

Calibration — base goals :
```bash
python -m src.domain.evaluation.calibrate_base_goals --min-year 2000
```
Fichier produit : `outputs/calibration/base_goals.json` (Exemple: `{"baseGoals": 1.37}`)

Calibration — scale search :
```bash
python -m src.domain.evaluation.calibrate_scale --min-year 2000
```
Fichier produit : `outputs/calibration/scale_search.json` (Exemple: `{"best_scale": 800, "log_loss": 0.972}`)

*(Commandes de vérification PowerShell rapides : `Test-Path outputs\calibration\base_goals.json` etc.)*

### 3) Backtest

```bash
python -m src.domain.evaluation.model_backtest --min-year 2000 --max-matches 1000
```
Calcul : Log Loss, Brier Score, Calibration Curve.
Fichier produit : `reports/backtests/V1_backtest.json`

### 4) Snapshot pré-tournoi (Monte Carlo)

S'assurer d'abord que `src/data/raw/real_results.json` contient une structure vide (ou initiale).

Le script `run_monte_carlo` expose les options principales suivantes :
- `--n` : nombre de simulations (entier). Exemple `--n 1500`.
- `--base-goals` : valeur float pour les buts de base (défaut 1.35). Si laissé par défaut, le script tente de lire `outputs/calibration/base_goals.json`.
- `--scale` : valeur float pour le scale (défaut 800.0). Si laissé par défaut, le script tente de lire `outputs/calibration/scale_search.json`.
- `--mode` : `pre_tournament` (ignore `real_results.json`) ou `live` (applique `real_results.json`).
- `--model-version` : version du modèle (ex. `V1`).
- `--no-save` : si présent, n'enregistre pas le snapshot.

Exemple recommandé (1500 simulations pré-tournoi avec Dixon-Coles) :
```powershell
python -m src.domain.simulation.run_monte_carlo --n 1500 --mode pre_tournament --model-version V3
```
*(Vous pouvez augmenter `--n` ex. `10000` pour des runs haute-fidélité, attention au temps d'exécution. Grâce au traitement parallèle Multi-Core implémenté en Phase 2, 10 000 itérations sont extrêmement rapides).*

Autres comportements de la commande :
- `python -m src.domain.simulation.run_monte_carlo` : Exécute avec les valeurs par défaut (`--n=1000`, `--mode=pre_tournament`, `--model-version=V1`). Lit automatiquement les fichiers de calibration existants. Génère un snapshot dans `outputs/snapshots`.
- `python -m src.domain.simulation.run_monte_carlo --n 1000 --mode pre_tournament --model-version V3` : Utilise le modèle Dixon-Coles.
- Répéter ces commandes produit de nouveaux snapshots (timestamps différents). Les résultats varient au hasard entre runs (Monte-Carlo).

Points importants sur le snapshot :
- `--mode pre_tournament` vs `--mode live` :
  - `pre_tournament` ignore `real_results.json` (on simule tout).
  - `live` applique les résultats réels présents dans `real_results.json`, le nom du snapshot reflètera la phase.
- Coût en temps : (linéaire avec `--n`). `--n=1000` prend environ ~15-20s.

Fichiers produits attendus :
- `outputs/snapshots/snapshot_XXX_pre_tournament.json`
*(Vérification rapide : `Get-ChildItem outputs\snapshots -File | Sort-Object LastWriteTime -Descending | Select-Object -First 5`)*

Ce snapshot devient la référence.

### 5) Comparaison de modèles (Optionnel)

L'utilitaire `model_comparison.py` compare plusieurs versions de modèles en lançant des simulations Monte Carlo pour chacune.

```powershell
python -m src.domain.evaluation.model_comparison --models V1,V1_5,V2 --n 1000 --mode pre_tournament
```
- `--models` : liste de versions (séparées par des virgules).
- `--n` : nombre de simulations par modèle.
- `--output` : chemin de sortie (défaut `outputs/model_comparisons/all_model_results.json`).

*(Conseil : commencez par un `--n` modéré (1000) pour vérification).*

### 6) Lancer l'application Web (Front React + API FastAPI)

Pour lancer la nouvelle interface Premium :

1. Lancez l'API Backend (depuis la racine) :
```bash
uvicorn api.main:app --reload --port 8000
```

2. Lancez le Front-End (depuis le dossier `web`) :
```bash
cd web
npm run dev
```
Ouvrez l'URL locale (ex: `http://localhost:5173`) dans votre navigateur. À partir de là, toute la suite peut être pilotée depuis l'application web.

---

## Phase B : Routine à répéter pendant le tournoi (Journée par Journée)

Cette procédure est répétée après chaque journée.
**Attention : Ne pas éditer les JSON (`real_results.json`) à la main.**

### 1) Ajouter les résultats réels
Dans la nouvelle application Web (Onglet **Admin Live**).
Exemple : *Mexique 2–1 Afrique du Sud*.
Saisissez les identifiants et les scores, puis cliquez sur **Sauvegarder le Match**.
L'API Backend met à jour automatiquement `real_results.json`.

### 2) Construire l'état courant
L'application lance automatiquement la logique pour figer les matchs joués (`freeze_matches()`) et reconstruire l'état courant (matchs joués, matchs restants, classement actuel, bracket actuel, Elo/FIFA).

### 3) Mise à jour Elo/FIFA
Si activée, l'application exécute la mise à jour (ex. `update_elo_after_result()`) après les résultats de la journée.

### 4) Nouvelle simulation Monte Carlo
Depuis l'app ou en ligne de commande, relancer sur les matchs restants :
```bash
python -m src.domain.simulation.run_monte_carlo --n 10000 --mode live
```

### 5) Nouveau snapshot
Un nouveau snapshot est sauvegardé automatiquement (ex: `outputs/snapshots/snapshot_001_after_matchday1.json`).

### 6) Delta Tracker et Historique
L'application compare automatiquement le snapshot avant et après (Delta Tracker) et produit des deltas sous `reports/deltas/`. L'historique des résultats Monte Carlo, Elo, et FIFA est également conservé.

---

## Conseils opérationnels et Dépannage rapide

- **Modules vides / Attributs manquants :** Si un module Python a l'air vide après une modification, supprimez `__pycache__` et `.pyc`, puis redémarrez le terminal.
- **Fichiers manquants :** Toujours vérifier les chemins de sortie. Si un fichier manque, relancez l'étape correspondante.
- **Runs longs (10k+) :** Exécutez la commande dans un terminal détaché ou un job background et redirigez la sortie vers un fichier de log :
  ```bash
  python -m src.domain.simulation.run_monte_carlo --n 20000 --mode pre_tournament > montecarlo_20000.log 2>&1 &
  ```

### Les deux types d'adaptation (Apprentissage vs Recalibration)

Il est crucial de distinguer deux mécaniques d'adaptation pendant la compétition :

**1. L'Apprentissage Actif par "Live Elo" (L'adaptation des équipes - ACTIF)**
Afin de rendre les probabilités ultra-réalistes, le moteur intègre un système de "backward propagation" basé sur les Deltas, enrichi par des standards de data science sportive avancés :
- **Backward Propagation :** À chaque match joué, le moteur calcule le Delta entre le score attendu et le résultat final, et l'utilise pour rétropropager la force (Elo) des équipes.
- **Dynamic K-Factor (Momentum & Enjeu) :** La vitesse d'apprentissage s'adapte à l'importance du match. Les matchs de poule utilisent un `K=40`, tandis que les matchs à élimination directe utilisent un `K=60`. Les exploits sous forte pression sont ainsi sur-récompensés.
- **Margin of Victory (Marge de Victoire) :** Le modèle prend en compte l'écart de buts réel via une fonction d'amortissement algorithmique (G-Factor). Gagner 4-0 confère un bien plus gros boost d'Elo que de gagner 1-0.
- Les équipes s'échangent des points en temps réel : un exploit inattendu va propulser l'Elo d'une équipe vers le haut de manière permanente pour le reste du tournoi.

**2. La Recalibration Paramétrique Globale (Le Mode Adaptatif - DÉSACTIVÉ)**
Il s'agit de recalculer les règles mathématiques globales du tournoi (`baseGoals` et `scale`) en plein milieu de la compétition, au lieu d'utiliser celles calculées sur les 20 dernières années.
- Bien que le code puisse le faire techniquement, ce mode n'est pas automatisé.
- **Pourquoi ?** C'est très dangereux mathématiquement (risque majeur d'*overfitting*). Si les 5 premiers matchs finissent à 0-0 par hasard, l'algorithme global va paniquer et diviser la moyenne de buts par deux pour tout le reste de la Coupe du Monde. Il faut des milliers de matchs pour calibrer ces paramètres de façon fiable.

**3. Le Modèle Dixon-Coles (V3) et le God Mode (Chocs Elo)**
Outre la recalibration de l'Elo naturel, le moteur offre un contrôle total pour la prospective :
- **Dixon-Coles (V3)** : Le moteur corrige la probabilité des matchs nuls à l'aide d'un facteur de covariance ($\rho = -0.13$), brisant l'indépendance de la loi de Poisson pour un réalisme ultime des matchs à faible score.
- **God Mode** : Possibilité d'appliquer un choc d'Elo manuel (`elo_deltas`) à n'importe quelle équipe avant la simulation pour étudier l'impact d'une blessure ou d'une surprise.

### Ce que tu fais réellement en pratique pendant le tournoi

Une fois le projet terminé, ton travail quotidien pendant le tournoi se résume à une boucle de deux étapes depuis l'onglet **Admin Live** :

**1. Saisir les nouveaux scores**
Sélectionner le ou les matchs joués dans le menu déroulant, entrer les buts et cliquer sur **Sauvegarder le Score**.
*Attention : Cette action se contente d'enregistrer la vérité historique dans `real_results.json` pour la persistance. Rien d'autre ne se déclenche à ce moment-là pour vous permettre d'entrer plusieurs scores d'affilée.*

**2. Mettre à jour la plateforme**
Une fois tous les scores de la journée saisis, configurer les paramètres de la simulation (Modèle V3, Nombre d'itérations, éventuels Chocs Elo du God Mode) et cliquer sur le bouton **Lancer le Monte Carlo**.
C'est cette action qui agit comme une baguette magique :
- Elle fige les matchs joués (ex: si la France a gagné, elle a 100% de chance d'avoir gagné).
- Elle met à jour les classements Elo locaux (le cache MD5 permet de ne pas recalculer les Elos passés inutilement).
- Elle applique les chocs Elo (God Mode) si vous en avez paramétré.
- Elle lance une lourde simulation (ex: 10 000 itérations réparties sur vos CPU) sur *uniquement le reste du tournoi à jouer*.
- Elle génère un Snapshot avec ses intervalles de confiances.

**Quels onglets vont changer ?**
Une fois la tâche en arrière-plan terminée, l'ensemble de l'interface se met à jour :
- **Scores Live** : Le classement des poules intègre les nouveaux points/différences de buts.
- **Prédictions / Dashboard** : L'arbre des probabilités est entièrement re-dessiné.
- **Deltas** : Affiche mathématiquement l'impact du match que vous venez de rentrer (ex: +10% de chances de victoire finale pour l'équipe gagnante).
- **Historique** : Un nouveau Snapshot apparaît, prouvant la mise à jour du système.

Tu passes ainsi d'un simple simulateur à une véritable plateforme de suivi probabiliste en temps réel.

---

