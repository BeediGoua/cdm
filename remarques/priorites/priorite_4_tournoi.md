# Priorité 4 : Moteur Tournoi

## 1. Objectif
Construire la logique métier qui permet de gérer les conséquences des matchs de poules : calculer le classement de chaque groupe, identifier les meilleurs troisièmes, et positionner toutes les équipes qualifiées dans l'arbre de la phase finale (Round of 32).

## 2. Fichiers et Fonctions Créés
J'ai créé trois fichiers clés dans le dossier `src/domain/tournament/` :

1. **`compute_group_standings.py`**
   - Calcule les points (Victoire: 3, Nul: 1, Défaite: 0), la différence de buts, et les buts marqués pour chaque équipe.
   - Trie les équipes selon les critères MVP (Points > Diff de Buts > Buts > Aléatoire).
2. **`rank_third_placed.py`**
   - Collecte les 12 équipes ayant fini à la 3ème place de leur groupe respectif.
   - Les trie avec la même logique que les groupes.
   - Sélectionne les **8 meilleures équipes** pour le repêchage.
3. **`build_bracket.py`**
   - Charge le fichier `bracketRules.json`.
   - Assigne automatiquement les vainqueurs et les deuxièmes de groupes dans l'arbre (ex: `1A`, `2B`).
   - Utilise un algorithme de *backtracking* pour résoudre l'attribution complexe des 8 meilleurs troisièmes. Par exemple, le match `M074` (1E vs 3A/B/C/D/F) doit se voir attribuer une équipe de la liste sans qu'elle soit déjà prise par un autre match. L'algorithme trouve toujours la combinaison parfaite.

> [!NOTE]
> J'ai également écrit un petit script `scripts/fix_bracket.py` pour corriger les erreurs de syntaxe dans votre `bracketRules.json` (`"B"` est devenu `"3B"`).

## 3. Script de Validation Globale
J'ai rédigé un script `scripts/test_tournament_engine.py` qui génère des matchs au hasard pour simuler une phase de poule complète, classe les groupes, filtre les troisièmes et initialise le *Round of 32*. Tout s'exécute parfaitement, chaque équipe trouve correctement sa place dans le tableau final sans doublon.

## 4. Prochaines Étapes
Maintenant que le moteur du tournoi sait "classer et qualifier", la **Priorité 5 : Monte Carlo** consistera à regrouper tout ce code dans une boucle qui répète le processus 10 000 fois pour obtenir les probabilités globales de qualification de chaque nation.
