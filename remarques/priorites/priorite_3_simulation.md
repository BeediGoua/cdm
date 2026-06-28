# Priorité 3 : Simulation d'un match

## 1. Objectif
Le but de cette étape est de consommer le modèle mathématique de Poisson (développé à la priorité 2) pour l'appliquer à la simulation concrète d'un match. Il s'agit de passer des pourcentages théoriques au tirage au sort d'un score réaliste.

## 2. Fichiers et Fonctions Créés
J'ai créé le fichier :
`src/domain/simulation/simulate_match.py`

Il contient les deux modes nécessaires à la modélisation :

1. **`predict_match(elo_a, elo_b, base_goals, scale)`**
   - **Mode Distribution :** Cette fonction ne tire pas de hasard. Elle appelle simplement `compute_lambdas` puis `match_probabilities` du modèle Poisson pour retourner les probabilités brutes (Victoire, Nul, Défaite).
   - **Pourquoi :** Très utile pour l'affichage (ex: donner au joueur les probabilités de la rencontre avant de la simuler) et pour calibrer/vérifier le modèle via des métriques comme le Brier Score.

2. **`sample_match_score(elo_a, elo_b, base_goals, scale, max_goals=10)`**
   - **Mode Random :** C'est le cœur de la simulation. La fonction aplatit la matrice des probabilités des scores pour en faire une roue de loterie géante (chaque score a une portion de la roue proportionnelle à sa probabilité). Puis, un tirage au sort `random.choices()` est effectué pour ressortir un score exact (ex: `2-1`).
   - **Pourquoi :** C'est ce qui introduit la variance. Même si la France a 60% de chances de gagner contre le Canada, le tirage peut tomber sur les 21% de chances de faire un match nul `1-1`. Sans cela, Monte Carlo ne servirait à rien car le favori gagnerait toujours.

## 3. Utilité et Utilisation Future
Ce module est la brique unitaire de notre tournoi. 

Lors de l'exécution de la **Priorité 4 (Moteur tournoi)** et de la **Priorité 5 (Monte Carlo)** :
- Nous allons charger la liste complète des matchs d'un groupe.
- Pour chaque match, nous utiliserons `sample_match_score()` pour obtenir le score final.
- Avec ces scores, nous pourrons calculer les points (3 points victoire, 1 nul) et la différence de buts, pour ainsi classer les équipes.

La priorité 3 clôture la boucle de l'échelle d'un "match isolé". La suite du projet consistera à empiler plusieurs matchs pour en faire un "tournoi".
