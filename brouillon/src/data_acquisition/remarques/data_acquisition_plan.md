# Data Acquisition Plan - World Cup 2026

## Objectif

Rassembler les données nécessaires pour la version initiale du simulateur :

- structure officielle du tournoi
- équipes qualifiées
- calendrier des matchs et stades
- classement FIFA actuel
- ratings Elo des équipes
- historique des matchs pour calibration
- données de résultats réels pour live update

## Ce qui est déjà en place

- `src/data_acquisition/fetch_data.py` : pipeline de téléchargement des sources brutes
- `src/data_acquisition/normalize_data.py` : pipeline de normalisation initiale
- `src/data_acquisition/data_sources.py` : définitions des URLs et chemins de fichiers
- `src/data_acquisition/README.md` : documentation d’usage
- `src/data/raw/elo_ratings_manual.json` : template de fallback Elo manuel
- fichiers normalisés cibles vides dans `src/data/normalized/`

## Sources à récupérer en priorité

1. FIFA Ranking API (`fifa_rankings_current.json`)
2. OpenFootball 2026 (`cup.txt`, `cup_finals.txt`, `cup_stadiums.csv`, `quali_playoffs.txt`)
3. FootballRatings Elo (`footballratings_elo.html` et extraction vers CSV)
4. Historique des résultats internationaux (Kaggle / martj42)
5. Fichier manuel de fallback Elo pour les équipes manquantes

## Format de sortie attendu

- `src/data/raw/` : copies brutes des sources
- `src/data/normalized/` : assets prêts à être consommés par le moteur

### Assets normalisés

- `teams.json`
- `groups.json`
- `groupMatches.json`
- `venues.json`
- `bracketRules.json`

## Prochaines étapes

1. exécuter `python src/data_acquisition/fetch_data.py`
2. vérifier les fichiers dans `src/data/raw/`
3. exécuter `python src/data_acquisition/normalize_data.py`
4. remplir les données manquantes de `elo_ratings_manual.json` et `historical_results.csv`
5. enrichir `normalize_data.py` avec des parsers plus précis selon le format réel des fichiers
