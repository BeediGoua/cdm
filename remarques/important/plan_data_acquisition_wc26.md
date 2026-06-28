Voici la version fusionnée, réorganisée et complète.

Plan consolidé de data acquisition - Coupe du Monde 2026

0. Objectif du projet

L’objectif est de construire un simulateur probabiliste de Coupe du Monde 2026 basé sur :

données officielles tournoi
+ FIFA Ranking API
+ Elo
+ modèle Poisson
+ simulation Monte Carlo
+ mise à jour progressive pendant le tournoi

La première version doit répondre à quatre questions :

1. Quelles équipes participent ?
2. Dans quels groupes jouent-elles ?
3. Quels matchs doivent être simulés ?
4. Quelle est la force initiale de chaque équipe ?

Si ces quatre blocs sont propres, nous pouvons construire :

moteur de poules
bracket
classement des meilleurs troisièmes
modèle Elo-Poisson
Monte Carlo
dashboard probabiliste
live update

⸻

1. Évolution du plan initial

Au départ, le plan était :

FIFA officielle
+ FIFA Ranking API
+ Elo manuel
+ martj42 international_results

Puis les tests ont ajouté deux sources importantes :

FootballRatings.org
OpenFootball 2026

Donc la V1 devient plus solide :

FIFA Ranking API
+ FootballRatings Elo
+ OpenFootball 2026
+ martj42 historical results
+ Elo manuel fallback

Wikipédia sort du pipeline principal, car les tests ont donné :

403 Forbidden

Décision :

Wikipedia = optionnel
FIFA / OpenFootball = sources principales pour la structure tournoi

⸻

2. Sources retenues

Source 1 : FIFA officielle

Rôle :

structure officielle du tournoi
groupes
calendrier
stades
bracket
règles de qualification
règles de départage

Utilisation :

src/data/normalized/groups.json
src/data/normalized/playoffs.json
src/data/normalized/groupMatches.json
src/data/normalized/venues.json
src/data/normalized/bracketRules.json

C’est la source de vérité pour la logique tournoi. Même si OpenFootball nous aide à récupérer les fichiers plus vite, les informations doivent rester cohérentes avec FIFA.

⸻

Source 2 : FIFA Ranking API

Endpoint validé :

https://api.fifa.com/api/v3/rankings/?gender=1&count=211

Rôle :

rang FIFA
points FIFA
rang précédent
points précédents
confédération
drapeaux
identifiants FIFA

Fichiers générés :

src/data/raw/fifa_rankings_current.json
src/data/normalized/fifa_rankings_current.json

Utilisation finale :

src/data/normalized/teams.json
src/domain/prediction/teamStrength.ts
src/domain/live/updateFifaRatingAfterResult.ts
src/features/dashboard/FifaRankingTable.tsx

Exemple normalisé :

{
  "id": "fra",
  "fifaCode": "FRA",
  "nameEn": "France",
  "fifaTeamId": "43946",
  "fifaRank": 1,
  "previousFifaRank": 3,
  "fifaPoints": 1877.32,
  "previousFifaPoints": 1870.0,
  "confederation": "UEFA",
  "flagUrl": "https://api.fifa.com/api/v3/picture/flags-sq-2/FRA"
}

⸻

Source 3 : FootballRatings.org

Résultat des tests :

status_code = 200
rows_found = 12
ratings as of 8 June 2026
244 teams visibles sur le site

Le fichier footballratings_elo.csv contient déjà :

Spain        2155
Argentina    2114
France       2062
England      2021
Brazil       1991
Portugal     1986
Colombia     1982
Netherlands  1944
Ecuador      1938
Germany      1932
Norway       1914
Croatia      1911

Conclusion :

FootballRatings.org devient la source Elo prioritaire.

Limite :

Le parser actuel ne récupère que 12 équipes.
Le site affiche "Loading more teams..."
Les autres équipes sont probablement chargées via JavaScript.

Donc pour la V1 :

FootballRatings = Elo automatique partiel
Elo manuel = fallback pour compléter les équipes manquantes

Fichiers :

src/data/raw/footballratings_elo.csv
src/data/raw/elo_ratings.csv
src/data/normalized/teams.json

Exemple final dans teams.json :

{
  "id": "fra",
  "nameEn": "France",
  "fifaRank": 1,
  "fifaPoints": 1877.32,
  "elo": 2062,
  "eloRank": 3,
  "eloSource": "footballratings.org",
  "eloDate": "2026-06-08"
}

⸻

Source 4 : Elo manuel fallback

Pourquoi garder Elo manuel ?

Parce que FootballRatings ne donne pas encore les 48 équipes avec notre parser actuel.

Fichier :

src/data/raw/elo_ratings_manual.json

Structure :

[
  {
    "teamId": "fra",
    "teamName": "France",
    "elo": 2062,
    "rank": 3,
    "source": "manual",
    "date": "2026-06-09"
  }
]

Règle d’utilisation :

si Elo existe dans FootballRatings -> utiliser FootballRatings
sinon -> utiliser elo_ratings_manual.json
sinon -> elo = null

Pseudo-code :

elo = footballratings_elo.get(teamName)
if elo is None:
    elo = manual_elo.get(teamId)
team["elo"] = elo

Utilisation :

src/domain/prediction/teamStrength.ts
src/domain/prediction/expectedGoals.ts
src/domain/live/updateEloAfterResult.ts

⸻

Source 5 : OpenFootball 2026

Les anciens liens OpenFootball étaient faux.

À remplacer définitivement par :

OPENFOOTBALL_RAW_CANDIDATES = [
    "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/cup.txt",
    "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/cup_finals.txt",
    "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/cup_stadiums.csv",
    "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/quali_playoffs.txt",
]

Résultat des tests :

status_code = 200
looks_like_football_txt = True

Donc OpenFootball est exploitable.

cup.txt

Contient :

World Cup 2026
104 matches
48 teams
16 host cities
group stage
matchdays
fixtures
stades
villes
horaires

Utilisation :

src/data/raw/openfootball_cup.txt
src/data/normalized/groupMatches.json
src/data/normalized/groups.json

⸻

cup_finals.txt

Contient :

Round of 32
match 73
match 74
slots 1A, 2A, 3A/B/C/D/F
W74
L101

Utilisation :

src/data/raw/openfootball_cup_finals.txt
src/data/normalized/bracketRules.json

C’est probablement le fichier le plus important pour éviter les erreurs de bracket.

Exemple brut :

(74) 16:30 UTC-4  1E v 3A/B/C/D/F @ Boston

Sortie attendue :

{
  "id": "M74",
  "round": "R32",
  "homeSlot": "1E",
  "awaySlotOptions": ["3A", "3B", "3C", "3D", "3F"],
  "venue": "Boston",
  "time": "16:30",
  "timezone": "UTC-4"
}

⸻

cup_stadiums.csv

Contient :

city
timezone
country code
stadium name
capacity
wikipedia
wikidata
coords

Utilisation :

src/data/raw/openfootball_stadiums.csv
src/data/normalized/venues.json

Exemple attendu :

{
  "id": "metlife",
  "city": "New York/New Jersey",
  "country": "us",
  "name": "MetLife Stadium",
  "capacity": 82500,
  "timezone": "UTC-4",
  "coords": "40°48′48″N 74°4′27″W"
}

⸻

quali_playoffs.txt

Contient :

UEFA play-offs
Path A
semi-finals
finals
scores
penalties

Utilisation :

src/data/raw/openfootball_quali_playoffs.txt
src/data/normalized/playoffs.json

Pour notre simulateur, ce fichier sert surtout à gérer les placeholders des barragistes.

⸻

Source 6 : martj42 international_results

Source :

https://github.com/martj42/international_results

Fichiers récupérés :

historical_results.csv
shootouts.csv
goalscorers.csv

Rôle :

évaluation
backtest
calibration
nettoyage historique
analyse des scores

Utilisation :

src/data/processed/matches_clean.csv
src/domain/evaluation/backtest.ts
src/domain/evaluation/logLoss.ts
src/domain/evaluation/calibration.ts
src/domain/prediction/poissonModel.ts

Cette source ne sert pas forcément à faire fonctionner le premier simulateur, mais elle sert à montrer que le modèle est sérieux et évalué.

Nettoyage nécessaire :

convertir date en datetime
supprimer les scores manquants
supprimer matchs non joués
normaliser noms équipes
créer total_goals
créer goal_diff
créer outcome
filtrer éventuellement après 2000 ou 2010

Sortie :

src/data/processed/matches_clean.csv

Colonnes propres :

date
home_team
away_team
home_score
away_score
tournament
neutral
home_win
draw
away_win
total_goals
goal_diff

⸻

Source 7 : International-football.net

Résultat des tests :

status_code = 200
rows_found = 0
international_football_elo.csv vide

Conclusion :

Ne pas utiliser International-football.net pour la V1.

On le garde comme source secondaire, mais on arrête de perdre du temps dessus maintenant.

⸻

3. OpenFootball quick-starter

Lien :

https://github.com/openfootball/quick-starter

Point important :

quick-starter n’est pas une base de données finale.
C’est un dépôt de démarrage pour convertir les données OpenFootball en JSON/CSV ou générer une base football.db.

Ce qui est pertinent :

Conversion .txt vers JSON

Commande exemple :

fbtxt2json england/2025-26/1-premierleague.txt -o en.1.json

Utilité :

transformer les fichiers OpenFootball en JSON propre
charger les fichiers dans Python / Gradio / React

⸻

Conversion .txt vers CSV

Commande exemple :

fbtxt2csv euro/2024--germany/euro.txt -o euro2024.csv

Colonnes générées :

League
Date
Time
Team 1
Team 2
Score
HT
FT
ET
P
Round
Ground

Utilité :

faire un dataset de matchs
calculer stats
extraire résultats
extraire phases
extraire stades
extraire équipes

Exemple d’exploitation :

import pandas as pd
df = pd.read_csv("euro2024.csv")
df = df.rename(columns={
    "Team 1": "home_team",
    "Team 2": "away_team",
    "FT": "score_ft",
    "Round": "round",
    "Ground": "stadium"
})
df["date"] = pd.to_datetime(df["Date"])

Puis :

home_team / away_team
→ table de normalisation noms équipes
→ Elo
→ FIFA Ranking
→ forme récente
→ probabilité victoire/nul/défaite

⸻

Templates disponibles

Dans datafile, on trouve notamment :

worldcup.rb
worldcup2014.rb
worldcup2018.rb
worldcup2022.rb
euro.rb
euro2024.rb
eng.rb
fr.rb
de.rb
es.rb
it.rb
cl.rb

Utilité :

référence pour Coupe du Monde
référence pour Euro
référence pour Ligue 1
référence pour Premier League
référence pour Champions League

Limite :

La partie SQLite / football.db est indiquée comme en cours de refonte.

Décision :

Pour notre projet :
OpenFootball .txt
→ parser Python maison ou fbtxt2csv / fbtxt2json
→ pandas
→ normalisation équipes
→ enrichissement Elo/FIFA
→ simulation

⸻

4. Architecture data consolidée

Avant :

src/data/raw/
  fifa_rankings_current.json
  historical_results.csv
  elo_ratings_manual.json

Maintenant :

src/
  data/
    raw/
      fifa_rankings_current.json
      historical_results.csv
      shootouts.csv
      goalscorers.csv
      elo_ratings_manual.json
      footballratings_elo.csv
      openfootball_cup.txt
      openfootball_cup_finals.txt
      openfootball_stadiums.csv
      openfootball_quali_playoffs.txt
    normalized/
      fifa_rankings_current.json
      teams.json
      groups.json
      playoffs.json
      groupMatches.json
      venues.json
      bracketRules.json
    processed/
      matches_clean.csv

⸻

5. Fichiers minimaux à produire

Pour commencer vraiment le projet :

src/data/normalized/teams.json
src/data/normalized/groups.json
src/data/normalized/playoffs.json
src/data/normalized/groupMatches.json
src/data/normalized/venues.json
src/data/normalized/bracketRules.json
src/data/raw/elo_ratings_manual.json
src/data/raw/footballratings_elo.csv
src/data/raw/fifa_rankings_current.json
src/data/raw/historical_results.csv
src/data/processed/matches_clean.csv

Le fichier central reste :

teams.json

Il fusionne :

FIFA Ranking
+ FootballRatings Elo
+ Elo manuel fallback
+ groupe Coupe du Monde
+ drapeau
+ confédération

Exemple final :

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

6. Pipeline de data acquisition consolidé

Étape 1 : récupérer FIFA Ranking API

Entrée :

https://api.fifa.com/api/v3/rankings/?gender=1&count=211

Sortie brute :

src/data/raw/fifa_rankings_current.json

Sortie normalisée :

src/data/normalized/fifa_rankings_current.json

But :

avoir toutes les équipes FIFA avec rang, points, confédération et drapeau

⸻

Étape 2 : récupérer OpenFootball 2026

Fichiers :

openfootball_cup.txt
openfootball_cup_finals.txt
openfootball_stadiums.csv
openfootball_quali_playoffs.txt

URLs :

OPENFOOTBALL_FILES = {
    "cup": "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/cup.txt",
    "cup_finals": "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/cup_finals.txt",
    "stadiums": "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/cup_stadiums.csv",
    "quali_playoffs": "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/quali_playoffs.txt",
}

Sorties :

src/data/raw/openfootball_cup.txt
src/data/raw/openfootball_cup_finals.txt
src/data/raw/openfootball_stadiums.csv
src/data/raw/openfootball_quali_playoffs.txt

But :

récupérer fixtures
stades
bracket final
barragistes

⸻

Étape 3 : récupérer FootballRatings Elo

Sortie :

src/data/raw/footballratings_elo.csv

Limite actuelle :

12 équipes récupérées seulement
parser à améliorer

But :

alimenter teamStrength.ts avec une source Elo plus robuste que le manuel

⸻

Étape 4 : compléter Elo manuel

Créer :

src/data/raw/elo_ratings_manual.json

Il doit compléter les équipes absentes de FootballRatings.

But :

avoir un Elo pour toutes les équipes de la Coupe du Monde

⸻

Étape 5 : récupérer martj42

Entrées :

results.csv
shootouts.csv
goalscorers.csv

Sorties :

src/data/raw/historical_results.csv
src/data/raw/shootouts.csv
src/data/raw/goalscorers.csv

Puis nettoyage :

src/data/processed/matches_clean.csv

But :

backtest
calibration
analyse des scores

⸻

Étape 6 : construire les fichiers normalisés tournoi

À partir de FIFA / OpenFootball :

groups.json
playoffs.json
groupMatches.json
venues.json
bracketRules.json

But :

donner au simulateur une structure tournoi propre

⸻

Étape 7 : construire teams.json

Fusionner :

fifa_rankings_current.json
footballratings_elo.csv
elo_ratings_manual.json
groups.json

Sortie :

src/data/normalized/teams.json

Règle :

1. Identité FIFA depuis FIFA Ranking API
2. Elo depuis FootballRatings si disponible
3. Elo depuis manuel si manquant
4. groupe depuis groups.json
5. drapeau depuis FIFA API

⸻

7. Code consolidé à ajouter

requirements.txt

requests
pandas
lxml
beautifulsoup4

⸻

URLs OpenFootball corrigées

OPENFOOTBALL_RAW_CANDIDATES = [
    "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/cup.txt",
    "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/cup_finals.txt",
    "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/cup_stadiums.csv",
    "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/quali_playoffs.txt",
]

⸻

Fonction d’acquisition OpenFootball

OPENFOOTBALL_FILES = {
    "cup": "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/cup.txt",
    "cup_finals": "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/cup_finals.txt",
    "stadiums": "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/cup_stadiums.csv",
    "quali_playoffs": "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/quali_playoffs.txt",
}
def acquire_openfootball_files():
    import requests
    from pathlib import Path
    raw_dir = Path("src/data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    for name, url in OPENFOOTBALL_FILES.items():
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        ext = "csv" if name == "stadiums" else "txt"
        out = raw_dir / f"openfootball_{name}.{ext}"
        out.write_text(r.text, encoding="utf-8")
        print(f"{name} sauvegardé -> {out}")

À appeler dans scripts/acquire_data.py :

def main():
    acquire_fifa_ranking()
    acquire_historical_results()
    acquire_openfootball_files()
    acquire_footballratings_elo()
    create_manual_elo_seed()
    clean_historical_results(min_year=2000)

⸻

Fonction d’acquisition FootballRatings

import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pathlib import Path
def acquire_footballratings_elo():
    url = "https://www.footballratings.org/"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,text/plain,*/*",
    }
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    text = BeautifulSoup(r.text, "html.parser").get_text("\n", strip=True)
    pattern = re.compile(
        r"#\s*(?P<rank>\d+)\s+"
        r"(?P<confed>[A-Z]{2,10})\s+View\s+"
        r"(?P<team>[A-Za-zÀ-ÿ\s\.\-']+?)\s+"
        r"Rating\s+(?P<rating>[\d,]+)\s+"
        r"Change\s+(?P<change>[+-]?\d+)",
        re.I
    )
    rows = []
    for m in pattern.finditer(text):
        rows.append({
            "rank": int(m.group("rank")),
            "confederation": m.group("confed"),
            "teamName": re.sub(r"\s+", " ", m.group("team")).strip(),
            "elo": int(m.group("rating").replace(",", "")),
            "change": int(m.group("change")),
            "source": url,
            "date": "2026-06-08",
        })
    df = pd.DataFrame(rows)
    out = Path("src/data/raw/footballratings_elo.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"FootballRatings Elo récupéré: {len(df)} lignes -> {out}")

⸻

Script d’acquisition complet : scripts/acquire_data.py

import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
BASE = Path("src/data")
RAW = BASE / "raw"
NORMALIZED = BASE / "normalized"
PROCESSED = BASE / "processed"
for p in [RAW, NORMALIZED, PROCESSED]:
    p.mkdir(parents=True, exist_ok=True)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; WC26DataBot/0.1)",
    "Accept": "application/json,text/html,text/plain,*/*",
}
FIFA_RANKING_URL = "https://api.fifa.com/api/v3/rankings/?gender=1&count=211"
RESULTS_URL = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
SHOOTOUTS_URL = "https://raw.githubusercontent.com/martj42/international_results/master/shootouts.csv"
GOALSCORERS_URL = "https://raw.githubusercontent.com/martj42/international_results/master/goalscorers.csv"
OPENFOOTBALL_FILES = {
    "cup": "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/cup.txt",
    "cup_finals": "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/cup_finals.txt",
    "stadiums": "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/cup_stadiums.csv",
    "quali_playoffs": "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/quali_playoffs.txt",
}
def save_json(path: Path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8"
    )
def get_team_name(team_name_list):
    if not isinstance(team_name_list, list):
        return None
    for item in team_name_list:
        if item.get("Locale") == "en-GB":
            return item.get("Description")
    return team_name_list[0].get("Description") if team_name_list else None
def normalize_fifa_team(row):
    code = row.get("IdCountry")
    return {
        "id": code.lower() if code else None,
        "fifaCode": code,
        "nameEn": get_team_name(row.get("TeamName")),
        "fifaTeamId": row.get("IdTeam"),
        "fifaRank": row.get("Rank"),
        "previousFifaRank": row.get("PrevRank"),
        "rankingMovement": row.get("RankingMovement"),
        "fifaPoints": row.get("DecimalTotalPoints"),
        "previousFifaPoints": row.get("DecimalPrevPoints"),
        "confederation": row.get("ConfederationName"),
        "rankingScheduleId": row.get("IdSchedule"),
        "matchesCount": row.get("Matches"),
        "flagUrl": f"https://api.fifa.com/api/v3/picture/flags-sq-2/{code}" if code else None,
    }
def acquire_fifa_ranking():
    r = requests.get(FIFA_RANKING_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    raw = r.json()
    rows = raw.get("Results", [])
    normalized = [normalize_fifa_team(row) for row in rows]
    save_json(RAW / "fifa_rankings_current.json", raw)
    save_json(NORMALIZED / "fifa_rankings_current.json", normalized)
    print(f"FIFA ranking récupéré: {len(normalized)} équipes")
def acquire_historical_results():
    results = pd.read_csv(RESULTS_URL)
    shootouts = pd.read_csv(SHOOTOUTS_URL)
    goalscorers = pd.read_csv(GOALSCORERS_URL)
    results.to_csv(RAW / "historical_results.csv", index=False)
    shootouts.to_csv(RAW / "shootouts.csv", index=False)
    goalscorers.to_csv(RAW / "goalscorers.csv", index=False)
    print(f"Historical results: {results.shape}")
    print(f"Shootouts: {shootouts.shape}")
    print(f"Goalscorers: {goalscorers.shape}")
def acquire_openfootball_files():
    for name, url in OPENFOOTBALL_FILES.items():
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        ext = "csv" if name == "stadiums" else "txt"
        out = RAW / f"openfootball_{name}.{ext}"
        out.write_text(r.text, encoding="utf-8")
        print(f"{name} sauvegardé -> {out}")
def acquire_footballratings_elo():
    url = "https://www.footballratings.org/"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,text/plain,*/*",
    }
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    text = BeautifulSoup(r.text, "html.parser").get_text("\n", strip=True)
    pattern = re.compile(
        r"#\s*(?P<rank>\d+)\s+"
        r"(?P<confed>[A-Z]{2,10})\s+View\s+"
        r"(?P<team>[A-Za-zÀ-ÿ\s\.\-']+?)\s+"
        r"Rating\s+(?P<rating>[\d,]+)\s+"
        r"Change\s+(?P<change>[+-]?\d+)",
        re.I
    )
    rows = []
    for m in pattern.finditer(text):
        rows.append({
            "rank": int(m.group("rank")),
            "confederation": m.group("confed"),
            "teamName": re.sub(r"\s+", " ", m.group("team")).strip(),
            "elo": int(m.group("rating").replace(",", "")),
            "change": int(m.group("change")),
            "source": url,
            "date": "2026-06-08",
        })
    df = pd.DataFrame(rows)
    out = RAW / "footballratings_elo.csv"
    df.to_csv(out, index=False)
    print(f"FootballRatings Elo récupéré: {len(df)} lignes -> {out}")
def create_manual_elo_seed():
    path = RAW / "elo_ratings_manual.json"
    if path.exists():
        print("elo_ratings_manual.json existe déjà")
        return
    data = [
        {
            "teamId": "fra",
            "teamName": "France",
            "elo": 2062,
            "rank": 3,
            "source": "manual",
            "date": datetime.utcnow().strftime("%Y-%m-%d")
        },
        {
            "teamId": "arg",
            "teamName": "Argentina",
            "elo": 2041,
            "rank": 4,
            "source": "manual",
            "date": datetime.utcnow().strftime("%Y-%m-%d")
        },
        {
            "teamId": "esp",
            "teamName": "Spain",
            "elo": 2054,
            "rank": 2,
            "source": "manual",
            "date": datetime.utcnow().strftime("%Y-%m-%d")
        }
    ]
    save_json(path, data)
    print("Seed Elo manuel créé")
def clean_historical_results(min_year=2000):
    df = pd.read_csv(RAW / "historical_results.csv")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "home_score", "away_score"])
    df["home_score"] = df["home_score"].astype(int)
    df["away_score"] = df["away_score"].astype(int)
    df["year"] = df["date"].dt.year
    if min_year:
        df = df[df["year"] >= min_year]
    df["total_goals"] = df["home_score"] + df["away_score"]
    df["goal_diff"] = df["home_score"] - df["away_score"]
    df["home_win"] = (df["home_score"] > df["away_score"]).astype(int)
    df["draw"] = (df["home_score"] == df["away_score"]).astype(int)
    df["away_win"] = (df["home_score"] < df["away_score"]).astype(int)
    cols = [
        "date",
        "year",
        "home_team",
        "away_team",
        "home_score",
        "away_score",
        "total_goals",
        "goal_diff",
        "home_win",
        "draw",
        "away_win",
        "tournament",
        "city",
        "country",
        "neutral",
    ]
    df = df[cols]
    df.to_csv(PROCESSED / "matches_clean.csv", index=False)
    print(f"matches_clean.csv créé: {df.shape}")
def main():
    acquire_fifa_ranking()
    acquire_historical_results()
    acquire_openfootball_files()
    acquire_footballratings_elo()
    create_manual_elo_seed()
    clean_historical_results(min_year=2000)
if __name__ == "__main__":
    main()

⸻

8. Formules Elo et FIFA

Créer :

src/domain/live/rating_formulas.py
def elo_expected_score(rating_a: float, rating_b: float, home_advantage: float = 0) -> float:
    dr = (rating_a + home_advantage) - rating_b
    return 1 / (10 ** (-dr / 400) + 1)
def elo_goal_difference_multiplier(goal_diff: int) -> float:
    n = abs(int(goal_diff))
    if n <= 1:
        return 1.0
    if n == 2:
        return 1.5
    return (11 + n) / 8
def update_elo_after_result(
    rating_a: float,
    rating_b: float,
    goals_a: int,
    goals_b: int,
    k: float = 60,
    home_advantage_a: float = 0,
):
    if goals_a > goals_b:
        w_a, w_b = 1.0, 0.0
    elif goals_a == goals_b:
        w_a, w_b = 0.5, 0.5
    else:
        w_a, w_b = 0.0, 1.0
    we_a = elo_expected_score(rating_a, rating_b, home_advantage_a)
    we_b = 1 - we_a
    g = elo_goal_difference_multiplier(goals_a - goals_b)
    delta_a = k * g * (w_a - we_a)
    delta_b = k * g * (w_b - we_b)
    return {
        "ratingA_before": rating_a,
        "ratingB_before": rating_b,
        "ratingA_after": rating_a + delta_a,
        "ratingB_after": rating_b + delta_b,
        "deltaA": delta_a,
        "deltaB": delta_b,
        "expectedA": we_a,
        "expectedB": we_b,
        "resultA": w_a,
        "resultB": w_b,
        "goalDiffMultiplier": g,
    }
def fifa_expected_score(points_a: float, points_b: float) -> float:
    dr = points_a - points_b
    return 1 / (10 ** (-dr / 600) + 1)
def update_fifa_points_after_result(
    points_a: float,
    points_b: float,
    goals_a: int,
    goals_b: int,
    importance: float,
):
    if goals_a > goals_b:
        w_a, w_b = 1.0, 0.0
    elif goals_a == goals_b:
        w_a, w_b = 0.5, 0.5
    else:
        w_a, w_b = 0.0, 1.0
    we_a = fifa_expected_score(points_a, points_b)
    we_b = 1 - we_a
    delta_a = importance * (w_a - we_a)
    delta_b = importance * (w_b - we_b)
    return {
        "pointsA_before": points_a,
        "pointsB_before": points_b,
        "pointsA_after": points_a + delta_a,
        "pointsB_after": points_b + delta_b,
        "deltaA": delta_a,
        "deltaB": delta_b,
        "expectedA": we_a,
        "expectedB": we_b,
        "resultA": w_a,
        "resultB": w_b,
    }

⸻

9. Utilisation des données dans le projet

teams.json

Utilisé par :

TeamBadge.tsx
GroupOverview.tsx
teamStrength.ts
simulateMatch.ts
ProbabilityTable.tsx

Rôle :

identité complète des équipes
force FIFA
force Elo
groupe
drapeau
confédération

⸻

groups.json

Utilisé par :

computeGroupStandings.ts
simulateGroupStage.ts
GroupOverview.tsx

Rôle :

savoir qui joue dans quel groupe

⸻

groupMatches.json

Utilisé par :

MatchPredictionTable.tsx
simulateGroupStage.ts
LiveUpdate.tsx

Rôle :

connaître les matchs à simuler ou à renseigner réellement

⸻

venues.json

Utilisé par :

SchedulePreview.tsx
MatchCard.tsx
VenueInfo.tsx

Rôle :

stades
villes
timezone
pays hôtes

⸻

bracketRules.json

Utilisé par :

buildSlotMap.ts
assignThirdPlacedTeams.ts
buildBracket.ts
simulateTournament.ts

Rôle :

construire la phase finale

C’est le fichier le plus sensible.

⸻

elo_ratings_manual.json

Utilisé par :

eloService.ts
teamStrength.ts
updateEloAfterResult.ts

Rôle :

force sportive initiale fallback

⸻

footballratings_elo.csv

Utilisé par :

eloService.ts
teamStrength.ts
teams.json

Rôle :

source Elo prioritaire

⸻

matches_clean.csv

Utilisé par :

backtest.ts
logLoss.ts
calibration.ts
poissonModel.ts

Rôle :

évaluer le modèle

⸻

10. Ordre d’exécution

python scripts/acquire_data.py

Après exécution, on doit avoir :

src/data/raw/fifa_rankings_current.json
src/data/raw/historical_results.csv
src/data/raw/shootouts.csv
src/data/raw/goalscorers.csv
src/data/raw/openfootball_cup.txt
src/data/raw/openfootball_cup_finals.txt
src/data/raw/openfootball_stadiums.csv
src/data/raw/openfootball_quali_playoffs.txt
src/data/raw/footballratings_elo.csv
src/data/raw/elo_ratings_manual.json
src/data/normalized/fifa_rankings_current.json
src/data/processed/matches_clean.csv

Ensuite, créer :

scripts/build_teams.py

qui fusionne :

fifa_rankings_current.json
footballratings_elo.csv
elo_ratings_manual.json
groups.json

en :

src/data/normalized/teams.json

⸻

11. Nouvelle stratégie V1

Ancienne stratégie :

FIFA Ranking API
+ martj42
+ Elo manuel
+ FIFA officielle manuelle

Nouvelle stratégie :

FIFA Ranking API
+ FootballRatings Elo
+ OpenFootball 2026
+ martj42
+ Elo manuel fallback

Rôle de chaque source :

FIFA Ranking API
= points FIFA, rang FIFA, drapeaux, confédérations
FootballRatings
= Elo actuel prioritaire
OpenFootball
= calendrier, stades, bracket, barrages
martj42
= historique pour backtest
Elo manuel
= compléter les équipes manquantes

⸻

12. Roadmap data

V1

FIFA Ranking API
FootballRatings Elo partiel
OpenFootball fixtures/stades/bracket
martj42 historique
Elo manuel fallback

Objectif :

faire tourner Poisson + Elo + FIFA

⸻

V1.5

améliorer parser FootballRatings
récupérer plus que les 12 premières équipes
normaliser OpenFootball en JSON complet
construire teams.json automatiquement

⸻

V2

historique FIFA par pays
features de tendance
rankingTrend1Year
pointsTrend1Year
rankVolatility

⸻

V3

xG
FBref
odds bookmakers
blessures
Transfermarkt
API-Football live

⸻

13. Verdict final

Les derniers tests améliorent fortement le projet.

On ne dépend plus seulement de :

FIFA Ranking API
+ Elo manuel

On peut maintenant s’appuyer sur :

FootballRatings.org
OpenFootball 2026

Conclusion opérationnelle :

1. OpenFootball devient la source pratique pour la structure tournoi.
2. FootballRatings devient la source prioritaire pour Elo.
3. FIFA Ranking API reste la source officielle pour points FIFA.
4. martj42 reste la source d’évaluation et calibration.
5. Elo manuel reste un fallback.
6. International-Football est mis de côté pour la V1.
7. Wikipédia reste optionnel.

C’est exactement le socle nécessaire pour une V1 sérieuse :

Poisson + Elo + FIFA + Monte Carlo
