# Guide Utilisateur - Application Web CDM 2026

Ce document explique les fonctionnalités de chaque onglet de l'application Web de simulation de la Coupe du Monde 2026. L'application est un tableau de bord analytique permettant d'interagir avec les résultats stochastiques du moteur Monte Carlo.

---

## 1. Dashboard (Tableau de Bord)
**Fichier :** `src/pages/Dashboard.tsx`
**Fonction principale :** La vue globale des grands favoris du tournoi.
* **Ce qu'on peut y faire :**
  * Voir le top 20 des équipes triées par probabilité de victoire finale.
  * Consulter les notes "Live Elo" et les points FIFA actuels.
  * **Changer de modèle** : Via le menu déroulant en haut à droite, basculer dynamiquement entre la vue "Comparaison" (affiche les barres de V1, V2, V3 côte à côte) et une vue détaillée d'un modèle spécifique (avec sa barre de progression de tournoi et ses intervalles de confiance à 95%).
  * Cliquer sur n'importe quelle équipe pour être redirigé vers sa vue détaillée (`TeamDetail`).

## 2. Labo H2H (MatchPrediction)
**Fichier :** `src/pages/MatchPrediction.tsx`
**Fonction principale :** Simuler un match spécifique entre deux équipes (Head-to-Head).
* **Ce qu'on peut y faire :**
  * Sélectionner une équipe à domicile et une équipe à l'extérieur via les grands menus déroulants.
  * Voir les notes Elo respectives et la différence de force mathématique.
  * **Sélectionner le modèle** (V1, V2, ou V3) pour observer comment l'approche stochastique modifie les probabilités de victoire, nul, ou défaite.
  * Visualiser les scores exacts les plus probables pour l'affrontement (ex: 1-0, 0-0, 2-1) en fonction de la matrice de distribution du modèle sélectionné.

## 3. Arbre (Bracket)
**Fichier :** `src/pages/Bracket.tsx`
**Fonction principale :** Le parcours vers la finale.
* **Ce qu'on peut y faire :**
  * Observer quelles équipes ont le plus de chances mathématiques d'atteindre chaque palier du tournoi (Huitièmes, Quarts, Demies, Finale, Vainqueur).
  * **Changer de modèle** : Filtrer avec la liste déroulante pour voir comment l'arbre change entre la V1 (Classique) et la V3 (Dixon-Coles).
  * Les pourcentages exacts de probabilité d'atteindre le palier sont affichés à côté de chaque équipe.

## 4. Bourse Elo (Power Rankings)
**Fichier :** `src/pages/PowerRankings.tsx` (ou `LiveElo.tsx`)
**Fonction principale :** Le classement brut de force (indépendant des simulations).
* **Ce qu'on peut y faire :**
  * Voir la force intrinsèque actuelle de chaque équipe générée par la fonction logistique (Phase 1 du moteur).
  * Suivre l'évolution historique de la note Elo d'une équipe au fur et à mesure que les vrais matchs du tournoi sont joués.

## 5. Deltas & Évolution
**Fichier :** `src/pages/Deltas.tsx`
**Fonction principale :** L'analyse des "Movers & Shakers" (Ceux qui montent et ceux qui chutent).
* **Ce qu'on peut y faire :**
  * Comparer le snapshot actuel avec le snapshot précédent (Dernier Match) ou le tout premier snapshot (Depuis le Début).
  * Observer les cartes **Top Gagnant** et **Top Perdant** pour voir qui a gagné/perdu le plus de probabilité de victoire après un match réel.
  * **Comparer les modèles pour 1 équipe** : Activer le mode "Comparaison", sélectionner une équipe (ex: France), et visualiser sur un graphique interactif l'évolution simultanée de ses chances selon la V1, V2 et V3 au fil du temps.
  * Changer la métrique observée (ex: regarder l'évolution des chances d'atteindre les Quarts plutôt que la Victoire).

## 6. Miracles (Upsets)
**Fichier :** `src/pages/Upsets.tsx`
**Fonction principale :** Le détecteur mathématique d'exploits (indépendant des simulations de Phase 3).
* **Ce qu'on peut y faire :**
  * Voir un classement des plus grandes surprises du tournoi réel.
  * Analyser le "Upset Score" : Un score généré en comparant le résultat réel d'un match avec la probabilité théorique d'avant-match calculée grâce à la Bourse Elo. Plus l'équipe était outsider, plus l'exploit est haut.

## 7. Scores & Matrice
**Fichier :** `src/pages/Scores.tsx`
**Fonction principale :** L'analyse microscopique de la Loi de Poisson.
* **Ce qu'on peut y faire :**
  * Voir une matrice visuelle (Heatmap) des probabilités de chaque score exact (ex: 2-1) moyennée sur l'ensemble du tournoi ou pour un scénario donné.
  * Observer la différence de densité entre un modèle Indépendant et un modèle Dixon-Coles (impact sur la probabilité des petits scores comme 0-0 ou 1-0).

## 8. Historique (Snapshots)
**Fichier :** `src/pages/History.tsx`
**Fonction principale :** La gestion des sauvegardes.
* **Ce qu'on peut y faire :**
  * Lister tous les "snapshots" (photographies statistiques) générés par le moteur Monte Carlo au fil du temps.
  * Chaque lancement depuis l'Admin Cockpit génère un nouveau snapshot horodaté visible ici.

## 9. Cockpit Admin
**Fichier :** `src/pages/AdminCockpit.tsx`
**Fonction principale :** Le centre de contrôle du moteur backend.
* **Ce qu'on peut y faire :**
  * **Lancer une simulation Monte Carlo** : Entrer le nombre d'itérations (ex: 10 000).
  * **Sélectionner le modèle à faire tourner** : V1 (Poisson Classique), V2 (Calibré), V3 (Dixon-Coles), ou le très puissant **ALL (Comparaison)** qui exécute les 3 modèles en parallèle grâce au multiprocessing.
  * Voir les logs en temps réel (Temps d'exécution, nombre de cœurs CPU utilisés, etc.)
  * Mettre à jour manuellement la "Bourse Elo" après la saisie de nouveaux résultats réels.

## 10. Documentation Scientifique
**Fichier :** `src/pages/Documentation.tsx`
**Fonction principale :** Le livre blanc théorique.
* **Ce qu'on peut y faire :**
  * Lire les justifications mathématiques des modèles de prédiction utilisés.
  * Comprendre les formules d'Espérance de Buts, d'ajustement de Dixon-Coles ($\rho = -0.13$), d'intervalles de confiance ($1.96 \times \sigma / \sqrt{N}$), et de la Règle de 3 pour l'incertitude sur les probabilités nulles.

## 11. Détail de l'Équipe (Team Detail)
**Fichier :** `src/pages/TeamDetail.tsx`
**Fonction principale :** La carte d'identité analytique d'une équipe.
* **Ce qu'on peut y faire :**
  * Voir toutes les statistiques d'une équipe spécifique (Historique des matchs, Elo, progression dans le tournoi).
  * Accessible en cliquant sur une équipe depuis le Dashboard.
