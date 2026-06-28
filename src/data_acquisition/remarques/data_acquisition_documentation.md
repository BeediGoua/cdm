# Documentation — Acquisition de données (World Cup 2026)

Résumé
------
Ce document décrit ce que nous avons implémenté pour l'acquisition des données : sources, extraction, validation, normalisation, stockage et import SQLite. Il explique les choix, les traitements automatisés et les fichiers importants du projet.

Sources et rôle
---------------
- FIFA Ranking API
  - Endpoint principal : `https://api.fifa.com/api/v3/rankings/?gender=1&count=211`
  - Rôle : source officielle pour le rang et les points FIFA. Sert à construire `teams.json` (identifiants FIFA, rangs, points, drapeaux).
- OpenFootball (GitHub raw)
  - Fichiers utilisés : `cup.txt`, `cup_finals.txt`, `cup_stadiums.csv`, `quali_playoffs.txt` (liens raw dans `src/data_acquisition/data_sources.py`)
  - Rôle : structure du tournoi (groupes, calendrier, stades, bracket). Fournit la base pour `groups.json`, `groupMatches.json`, `venues.json`, `bracketRules.json`, `playoffs.json`.
- FootballRatings.org
  - Rôle : source Elo prioritaire (parser partiel). Le site charge des équipes dynamiquement via JS; notre extracteur actuel récupère la partie HTML statique et génère `footballratings_elo.csv` si possible.
  - Fallback : `elo_ratings_manual.json` (manuel) si le parser n’a pas toutes les équipes.
- martj42 / international_results
  - Rôle : source historique principale pour backtests et calibration.
  - Nous essayons de télécharger `historical_results` depuis GitHub (martj42). Le pipeline teste plusieurs chemins et récupère `results.csv` si présent, le place dans `src/data/raw/historical_results.csv`.
- Wikipedia (optionnel)
  - Décision : exclu du pipeline principal (souvent bloqué par 403), possible source manuelle si besoin.

Scripts principaux
------------------
- `src/data_acquisition/fetch_data.py`
  - Téléchargement automatisé des sources (FIFA API, OpenFootball raw, FootballRatings HTML).
  - Détection et extraction HTML -> `footballratings_elo.csv` si possible.
  - Création d’un template `elo_ratings_manual.json` si absent.
  - Tentatives de récupération `historical_results` depuis `martj42` (plusieurs chemins) ; crée un placeholder si l’extraction échoue.
- `src/data_acquisition/validate_data.py`
  - Validation des fichiers raw (JSON, CSV, TXT, HTML).
  - Vérifie la présence d’en-têtes attendus et signale warnings/erreurs.
  - Autorise fallback `elo_ratings_manual.json` si `footballratings_elo.html` est manquant.
- `src/data_acquisition/normalize_data.py`
  - Convertit raw -> JSON normalisés :
    - `teams.json` : intègre FIFA ranking + Elo (FootballRatings ou manuel)
    - `groups.json` : composition des groupes (OpenFootball)
    - `groupMatches.json` : calendrier des poules (OpenFootball)
    - `venues.json` : stades (OpenFootball)
    - `bracketRules.json` : règles/bracket (parse de `cup_finals.txt`)
    - `playoffs.json` : barrages qualificatifs (parse de `quali_playoffs.txt`)
  - Nettoie et convertit `historical_results.csv` en `src/data/processed/matches_clean.csv` (colonnes standardisées, flags résultats, total_goals, goal_diff).
- `src/data_acquisition/import_sqlite.py`
  - Crée la base SQLite `src/data/processed/worldcup2026.db` et importe : `teams`, `groups`, `group_matches`, `venues`, `bracket_rules`.
- `src/data_acquisition/pipeline.py` et `src/data_acquisition/main.py`
  - Orchestrent le pipeline complet : acquisition → validation → normalisation → import SQLite.
  - `main.py` expose des flags pour sauter des étapes (`--no-fetch`, `--no-validate`, `--no-normalize`, `--no-import`).

Fichiers importants et but
-------------------------
- `src/data/raw/` (raw)
  - `fifa_rankings_current.json` : dump API FIFA (source officielle de rang/points)
  - `openfootball_cup.txt`, `openfootball_cup_finals.txt`, `openfootball_stadiums.csv`, `openfootball_quali_playoffs.txt` : structure tournoi
  - `footballratings_elo.html` / `footballratings_elo.csv` : extraction ELO (partielle)
  - `elo_ratings_manual.json` : fallback manuel pour ELO
  - `historical_results.csv` : fichier historique (téléchargé depuis martj42 `results.csv` si disponible, sinon placeholder)
- `src/data/normalized/` (produits normalisés)
  - `teams.json` : équipes normalisées (fifa + elo)
  - `groups.json` : mapping groupes -> teamIds
  - `groupMatches.json` : calendrier poules
  - `venues.json` : stades et méta
  - `bracketRules.json` : règles et matches des phases finales
  - `playoffs.json` : barrages qualificatifs
- `src/data/processed/` (résultats prêts à l’usage)
  - `matches_clean.csv` : historique nettoyé prêt au backtest
  - `worldcup2026.db` : base SQLite avec tables importées pour usage offline et requêtes rapides

Comment exécuter
----------------
Commande pipeline complète (depuis la racine du projet) :

```bash
python src/data_acquisition/main.py
```

Exécution par étapes :

```bash
python -m src.data_acquisition.fetch_data        # acquisition
python -m src.data_acquisition.validate_data     # validation
python -m src.data_acquisition.normalize_data    # normalisation
python -m src.data_acquisition.import_sqlite     # import SQLite
```

Ou via `main.py` en sautant des étapes :

```bash
python src/data_acquisition/main.py --no-fetch --no-validate
```

Limitations et notes
--------------------
- FootballRatings parser est partiel : le site charge la majorité des équipes via JavaScript. Pour l’améliorer, il faudrait un fetch côté headless (Playwright/selenium) ou utiliser une API alternative.
- Wikipedia a été exclu du pipeline principal à cause de 403 fréquents.
- `historical_results` : le dépôt martj42 expose `results.csv` à la racine (noté `results.csv`), le pipeline essaie plusieurs chemins et récupère ce fichier lorsqu’il est disponible. Si non disponible, un placeholder est créé.
- Validation signale des warnings si les CSV ne contiennent pas exactement les en-têtes attendus ; la normalisation tente malgré tout d’extraire les colonnes pertinentes.

Décisions clés
---------------
- Priorité aux sources officielles (FIFA) pour identifiants et rangs, OpenFootball pour structure de tournoi.
- FootballRatings pour l’ELO automatique tant que le parser donne des lignes exploitables ; sinon, `elo_ratings_manual.json` assure la complétude.
- martj42 choisi comme source historique car il contient un large historique structuré idéal pour backtests.

Prochaines améliorations recommandées
------------------------------------
- Améliorer l’extraction FootballRatings (headless JS) pour obtenir toutes les équipes.
- Ajouter tests unitaires pour chaque parser (`normalize_*`) et tests d’intégration pipeline.
- Documenter le mapping des noms d’équipes (alias) et améliorer `TEAM_NAME_ALIASES`.
- Ajouter métriques de qualité (nombre de matches historiques importés, teams sans ELO, etc.)

---

Fichier créé : `remarques/data_acquisition_documentation.md`

Si tu veux, je peux :
- Committer ce fichier et les changements dans une branche et créer une PR.
- Générer un petit notebook d’analyse sur `matches_clean.csv` pour vérifier la distribution des scores.

Que veux-tu que je fasse ensuite ?
