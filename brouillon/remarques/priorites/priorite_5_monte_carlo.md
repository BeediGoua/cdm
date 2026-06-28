# Priorité 5 : Monte Carlo

## 1. Objectif
Le but de cette étape est d'utiliser toutes les briques développées jusqu'ici pour simuler non pas un match, ni un tournoi, mais **10 000 tournois complets** afin de dégager des statistiques fiables sur les probabilités de chaque nation.

## 2. Fichiers et Fonctions Créés

J'ai structuré cette étape en deux fichiers dans `src/domain/simulation/` :

1. **`simulate_tournament.py`**
   - **Rôle :** Simule un parcours entier. 
   - **Déroulement :** Il commence par simuler tous les matchs de toutes les poules, appelle le `compute_group_standings` pour les classer, puis le `build_bracket` pour initialiser le "Round of 32". Ensuite, il boucle sur la phase finale, simule les matchs à élimination directe et enregistre le nom de chaque équipe qui passe au tour suivant (W73, W74...).
   - **Gestion des Nuls :** Si le simulateur sort un match nul en phase finale, un tirage 50/50 désigne le gagnant (simulant grossièrement les tirs au but pour ce MVP).
   - **Sortie :** Un dictionnaire associant chaque équipe au stade maximum qu'elle a atteint (ex: `{"fra": "champion", "can": "group"}`).

2. **`run_monte_carlo.py`**
   - **Rôle :** L'orchestrateur statistique.
   - **Déroulement :** Lance `simulate_tournament()` dans une boucle (par défaut $N=10 000$). Il tient des registres pour compter chaque fois qu'une équipe atteint un palier. Surtout, si une équipe est déclarée `champion`, le script comprend intelligemment qu'elle a aussi validé les paliers `final`, `semiFinal`, etc., et met tous ses compteurs à jour.
   - **Sortie :** Convertit les totaux en pourcentages et affiche un tableau des favoris du tournoi.

## 3. Résultats
Lors du premier essai, le script a fait tourner 1 000 tournois complets (soit des dizaines de milliers de matchs virtuels incluant des back-trackings d'arbres) en seulement **17 secondes**. Le modèle attribue logiquement aux favoris Elo comme la France ou l'Espagne de grandes chances (autour de 15-17%) de remporter la Coupe du Monde.

## 4. Conclusion
Le cœur du projet est officiellement fonctionnel ! 🚀
Nous avons un pipeline "Data > Elo > Poisson > Monte Carlo > Stats" entièrement fluide. 

La baseline **(V1)** est terminée. Les prochaines étapes consisteront à raffiner le modèle en ajoutant les ratings FIFA (V1.5) ou à calibrer `baseGoals` et `scale` de manière scientifique avec les données historiques martj42.
