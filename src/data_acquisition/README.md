# Acquisition de données pour le simulateur Coupe du Monde 2026

Ce dossier contient les scripts pour récupérer, valider, normaliser et importer les données du projet.

## Objectifs

- récupérer les données officielles FIFA pour la structure du tournoi, les groupes, les matchs, les stades et les classements
- récupérer les ratings Elo des équipes depuis eloratings.net (source 1) et international-football.net (source 2), avec fallback FIFA approx.
- stocker les fichiers bruts dans `src/data/raw/`
- créer les fichiers normalisés dans `src/data/normalized/`
- importer les données normalisées dans une base SQLite légère

## Sources principales

- FIFA Ranking API : `https://api.fifa.com/api/v3/rankings/?gender=1&count=211`
- Fichiers OpenFootball 2026 : `cup.txt`, `cup_finals.txt`, `cup_stadiums.csv`, `quali_playoffs.txt`
- World Football Elo : `https://www.eloratings.net/` (source primaire)
- Backup Elo : `https://www.international-football.net/elo-ratings-table` (source 2)
- FIFA Points fallback : approximation Elo depuis FIFA ranking points (fallback si sources Elo indisponibles)
- Team name overrides : `src/data/raw/team_name_overrides.json` pour résoudre les alias FIFA / noms officiels
- Dataset historique de matchs : Kaggle / martj42

## Structure des scripts

- `fetch_data.py` : téléchargement des sources brutes
- `validate_data.py` : vérification de la présence et du format des fichiers bruts
- `normalize_data.py` : génération des fichiers normalisés JSON
- `import_sqlite.py` : import des fichiers normalisés dans `src/data/processed/worldcup2026.db`
- `fetch_world_elo.py` : télécharge les Elo depuis eloratings.net et international-football.net
- `generate_footballratings_fallback.py` : génère `footballratings_elo_fallback.csv` à partir des points FIFA si sources Elo échouent- `pipeline.py` : orchestration des étapes
- `main.py` : point d’entrée unique pour lancer toute la pipeline

## Utilisation

Lancer la pipeline complète :

```bash
python src/data_acquisition/main.py
```

### Options

- `--no-fetch` : saute la phase d’acquisition des fichiers bruts
- `--no-validate` : saute la validation des fichiers bruts
- `--no-normalize` : saute la normalisation vers JSON
- `--no-import` : saute l’import dans SQLite

Exemple :

```bash
python src/data_acquisition/main.py --no-fetch --no-import
```

Cela exécute la validation et la normalisation uniquement, sans télécharger les sources ni importer la base.

## Validation

Le script `validate_data.py` vérifie :

- que chaque fichier attendu existe dans `src/data/raw/`
- que les JSON sont valides et contiennent les champs de base attendus
- que les CSV ont des en-têtes compatibles avec le format requis
- que les fichiers OpenFootball contiennent des groupes et des sections attendues
- que les fichiers Elo (world_football_elo.csv ou fallback) existent et contiennent des données valides

La validation est importante pour détecter les problèmes avant de normaliser ou d’importer les données.
Les équipes normalisées incluent désormais un champ `sourceConfidence` pour tracer si l'Elo provient d'une source primaire, secondaire, de backup ou d'un ajustement manuel.

> Note : le dépôt couvre aujourd’hui l’acquisition, la validation et la normalisation des données.
> Il ne comprend pas encore de moteur de simulation Monte Carlo ni de logique de live update du tournoi basée sur des résultats réels.
>
> Pour la suite, voir `remarques/WorldCup2026_Next_Steps_Live_Update.md`.

## Que faire si une source manque

- `fetch_data.py` crée un template pour `elo_ratings_manual.json` et un placeholder pour `historical_results.csv`
- `fetch_world_elo.py` tente d'accéder à eloratings.net et international-football.net; si les deux échouent, tu peux relancer `generate_footballratings_fallback.py` pour générer une approximation FIFA
- si une source n'est pas disponible, complète manuellement le fichier correspondant avant de relancer la pipeline

## Priorité des sources Elo

La normalisation (`normalize_data.py`) priorise les sources Elo dans cet ordre :
1. `src/data/raw/world_football_elo.csv` (eloratings.net ou international-football.net)
2. `src/data/raw/footballratings_elo_fallback.csv` (approximation FIFA Points)

Chaque Elo importé inclut un champ `elo_source` indiquant sa provenance pour traçabilité.
