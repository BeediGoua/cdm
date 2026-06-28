

# Simulateur Probabiliste - Coupe du Monde 2026

## Présentation du Projet

Ce projet est un simulateur statistique et prédictif complet dédié à la Coupe du Monde de la FIFA 2026. Conçu avec une approche scientifique rigoureuse, il s'appuie sur la loi des grands nombres (méthode de Monte-Carlo) et des modèles de distribution asymétriques pour évaluer en temps réel les probabilités de victoire, de qualification et d'élimination de chaque équipe nationale.

L'architecture du système est scindée en trois pôles principaux :
1. **Pipeline de Données (ETL)** : Extraction, nettoyage et normalisation des classements Elo, des points FIFA et des calendriers officiels.
2. **Moteur de Simulation Mathématique (Backend Python)** : Résolution probabiliste s'appuyant sur cinq itérations de modèles mathématiques, allant de la simple loi de Poisson indépendante jusqu'à une régression bivariée avec covariables dynamiques.
3. **Tableau de Bord Analytique (Frontend React)** : Interface utilisateur haut de gamme permettant l'interaction en direct avec le moteur (injection de scores réels, analyse de scénarios "What-If", suivi des deltas probabilistes).

---

## Modèles Mathématiques Implémentés

Le moteur probabiliste intègre plusieurs niveaux de complexité algorithmique, sélectionnables à la volée :

- **V1 - Poisson Indépendant (Classique)** : Modélisation standard postulant l'indépendance totale entre les buts marqués par l'équipe A et l'équipe B.
- **V2 - Poisson Calibré** : Modèle indépendant dont l'espérance de buts moyens et l'élasticité Elo sont ajustées historiquement sur les précédentes Coupes du Monde.
- **V3 - Modèle de Dixon-Coles (Réaliste)** : Introduction d'un paramètre de covariance permettant d'ajuster algébriquement la sur-occurrence empirique des matchs nuls à faible score (0-0, 1-1) générée par l'aversion au risque en fin de rencontre.
- **V4 - Modèle Bayésien Conjugué (Apprentissage en Ligne)** : Utilisation de l'inférence bayésienne (loi a priori Gamma conjuguée à la vraisemblance de Poisson) pour mettre à jour la force offensive et défensive d'une équipe en cours de tournoi.
- **V5 - Régression Bivariée avec Covariables (Modèle Moderne)** : Modèle temporel et contextuel ajustant l'espérance de buts en fonction de différentiels dynamiques (différence de buts cumulée et avantage de temps de récupération physique).

---

## Architecture du Dépôt

- `api/` : Code source de l'API RESTful développée avec FastAPI.
- `src/data_acquisition/` : Scripts de récupération et de formatage des données brutes (scrapping, APIs externes).
- `src/domain/` : Cœur algorithmique (modèles mathématiques, lois de distribution, simulateur de tournoi et de matchs).
- `src/data/` : Espace de stockage local des données brutes (`raw/`) et normalisées (`normalized/`).
- `scripts/` : Outils CLI d'administration, de validation d'intégrité et de backtesting.
- `web/` : Code source de l'application client (React, TypeScript, Vite).
- `outputs/` : Dossier de destination des calculs de calibration et des instantanés (snapshots) de probabilités générés par Monte-Carlo.

---

## Prérequis Techniques

Pour déployer et exécuter ce projet localement, les composants suivants sont requis :
- **Python 3.11** ou une version supérieure.
- **Node.js** (version LTS recommandée) et le gestionnaire de paquets npm.
- Un terminal compatible Bash ou PowerShell.

---

## Guide d'Installation

1. **Clonage et initialisation de l'environnement virtuel Python :**
   ```bash
   python -m venv .venv
   ```

2. **Activation de l'environnement virtuel :**
   - Sous Windows (PowerShell) :
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - Sous Linux / macOS (Bash) :
     ```bash
     source .venv/bin/activate
     ```

3. **Installation des dépendances Backend :**
   ```bash
   pip install -r requirements.txt
   ```

---

## Guide d'Utilisation

### 1. Acquisition et Préparation des Données
Avant de procéder à la moindre simulation, le moteur nécessite une base de données normalisée et vérifiée.

Lancer la pipeline d'acquisition (téléchargement et formatage) :
```bash
python src/data_acquisition/main.py
```

Valider l'intégrité stricte de la donnée générée :
```bash
python scripts/validate_data.py
```

### 2. Exécution d'une Simulation en Ligne de Commande (CLI)
Il est possible de solliciter le moteur de Monte-Carlo directement via le terminal. La commande suivante lance 10 000 itérations du tournoi complet en utilisant le modèle Dixon-Coles (V3) :

```bash
python -m src.domain.simulation.run_monte_carlo --n 10000 --mode pre_tournament --model-version V3
```
*Note : À l'issue du traitement, un rapport statistique détaillé est sauvegardé au format JSON dans le répertoire `outputs/snapshots/`.*

### 3. Démarrage de l'Application Web
L'application Web est composée de deux services devant fonctionner simultanément.

**Démarrage du Serveur API (Backend) :**
Dans le terminal principal, à la racine du projet :
```bash
uvicorn api.main:app --reload --port 8000
```

**Démarrage du Serveur de Développement (Frontend) :**
Dans un second terminal :
```bash
cd web
npm install
npm run dev
```

L'interface graphique est alors accessible via un navigateur web à l'adresse standard : `http://localhost:5173`.

---

## Maintenance Opérationnelle

Lors de modifications profondes de l'architecture du code Python, il est recommandé de purger les fichiers compilés en cache pour éviter toute régression fantôme.

Sous Windows (PowerShell) :
```powershell
Get-ChildItem -Path . -Recurse -Force -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -Force -Filter '*.pyc' | Remove-Item -Force -ErrorAction SilentlyContinue
```
Sous Linux / macOS :
```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```
