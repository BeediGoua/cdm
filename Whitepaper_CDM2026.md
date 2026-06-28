# Prédiction Stochastique de la Coupe du Monde de la FIFA 2026 : Une Approche par Loi de Poisson et Simulations de Monte Carlo

## 1. Introduction et Problématique

La prédiction des résultats sportifs, en particulier dans le football de très haut niveau, représente un défi statistique majeur en raison de la nature stochastique du jeu. Le faible nombre de buts par match rend les issues particulièrement sensibles aux événements aléatoires (cartons rouges, blessures, décisions arbitrales).

La **problématique centrale** de ce projet est la suivante : *Comment modéliser et prédire avec précision le déroulement et l'issue de la Coupe du Monde de la FIFA 2026, un tournoi au format inédit (48 équipes, 12 groupes), tout en réévaluant dynamiquement les probabilités de chaque équipe en temps réel au fil de la compétition ?*

Pour répondre à ce défi, nous avons développé une architecture logicielle prédictive combinant le système de classement **World Football Elo Ratings**, une modélisation par **Loi de Poisson** pour la génération de matrices de scores, et des évaluations à grande échelle via des **simulations de Monte Carlo**.

---

## 2. Cadre Théorique et Mathématique

### 2.1 Le Classement Elo comme Mesure d'Intensité Initiale

Le classement Elo fournit une évaluation continue, auto-correctrice et sans biais de la force relative de chaque équipe nationale. Contrairement au classement FIFA standard (parfois critiqué pour ses lenteurs d'adaptation), le système Elo réagit de manière proportionnelle à l'espérance de résultat.

Dans notre modèle, la force d'une équipe est représentée par son score Elo actuel ($E$). La différence de niveau entre deux équipes $A$ et $B$ dans un match donné est calculée par :
$$\Delta E = E_A - E_B$$

### 2.2 Modélisation de l'Espérance de Buts ($\lambda$)

Pour utiliser la loi de Poisson, il est nécessaire de définir l'espérance mathématique de buts (le paramètre $\lambda$) pour chaque équipe. Nous utilisons une fonction de transformation exponentielle permettant de convertir la différence Elo en espérance de buts attendus (Expected Goals) :

$$ \lambda_A = \text{base\_goals} \times \exp\left( \frac{\Delta E}{\text{scale}} \right) $$
$$ \lambda_B = \text{base\_goals} \times \exp\left( \frac{-\Delta E}{\text{scale}} \right) $$

**Paramètres calibrés :**
- **$\text{base\_goals}$** : L'espérance moyenne de buts par équipe par match lorsque les deux équipes sont de force parfaitement égale ($\Delta E = 0$). Les optimisations sur l'historique fixent généralement cette valeur autour de $1.35$.
- **$\text{scale}$** : Le facteur d'échelle (calibré via recherche sur grille autour de $800.0$) qui contrôle l'élasticité de la prédiction. Un *scale* plus faible rend le modèle plus déterministe (les favoris écrasent les outsiders), tandis qu'un *scale* plus élevé "aplatit" l'avantage et restitue la forte variance du football.

### 2.3 Loi de Poisson et Matrice de Scores

Une fois $\lambda_A$ et $\lambda_B$ obtenus, la probabilité pour une équipe de marquer exactement $k$ buts est donnée par la Fonction de Masse de Probabilité (PMF) de la loi de Poisson :

$$ P(X = k) = \frac{e^{-\lambda} \lambda^k}{k!} $$

Dans ce modèle de base, nous postulons l'indépendance statistique entre les buts marqués par $A$ et $B$. La probabilité d'un score exact $(i, j)$ est le produit des probabilités marginales :

$$ P(A=i \cap B=j) = \left( \frac{e^{-\lambda_A} \lambda_A^i}{i!} \right) \times \left( \frac{e^{-\lambda_B} \lambda_B^j}{j!} \right) $$

Pour déterminer les probabilités de victoire ($V_A$), de match nul ($N$) ou de défaite ($V_B$), le système somme ces probabilités sur une matrice de scores bornée (de $0$ à $10$ buts) :

- $P(V_A) = \sum_{i>j} P(A=i, B=j)$
- $P(N) = \sum_{i=j} P(A=i, B=j)$
- $P(V_B) = \sum_{i<j} P(A=i, B=j)$

### 2.4 Le Modèle de Dixon-Coles (Correction de l'Indépendance)

Le modèle de Poisson indépendant (Version 1 et 2) souffre d'une limitation mathématique bien documentée dans la littérature scientifique sportive : il sous-estime systématiquement la fréquence des matchs nuls à faible score (0-0, 1-1) et surestime légèrement les victoires étriquées (1-0, 0-1). En réalité, dans le football de haut niveau, le score n'est pas indépendant : si le match est à 0-0 à la 80ème minute, les deux équipes ont tendance à adopter des tactiques plus défensives.

Pour corriger ce biais, notre moteur intègre (en Version 3) le modèle de **Dixon-Coles (1997)**. Celui-ci introduit un paramètre de covariance $\rho$ (rho) qui ajuste spécifiquement la probabilité conjointe des scores faibles. La probabilité indépendante $P(X=i)P(Y=j)$ est multipliée par un facteur de correction $\tau(i,j)$ défini par :

- $\tau(0,0) = 1 - \lambda_A \lambda_B \rho$
- $\tau(1,0) = 1 + \lambda_A \rho$
- $\tau(0,1) = 1 + \lambda_B \rho$
- $\tau(1,1) = 1 - \rho$
- $\tau(x,y) = 1$ pour tous les autres scores.

Après une revue de la littérature appliquée au football moderne, nous avons fixé **$\rho = -0.13$**. Cette valeur négative gonfle algorithmiquement la probabilité des 0-0 et 1-1, ramenant le taux de matchs nuls du modèle à la réalité empirique observée lors des phases finales de Coupe du Monde (environ 25-28%).

### 2.4 Simulation de Monte Carlo et Règles Spécifiques du Tournoi

En raison de la complexité du format 2026 (12 groupes de 4 équipes, qualification des deux premiers et repêchage des 8 meilleurs troisièmes), le calcul combinatoire ou analytique est computationnellement intraitable. 

Nous appliquons donc la **méthode de Monte Carlo**. L'algorithme (`simulate_tournament.py`) exécute l'intégralité du tournoi $N$ fois (ex: $N = 10,000$).
Lors de la simulation, le modèle implémente rigoureusement les règles de "tie-breaking" de la FIFA, notamment pour départager les troisièmes de groupe (`rank_third_placed.py`) dans l'ordre strict suivant :
1. Points
2. Différence de Buts Globale
3. Buts Marqués (Goals For)
4. Facteur Aléatoire (remplaçant le tirage au sort / fair-play pour la modélisation)

En vertu de la Loi des Grands Nombres, la fréquence empirique d'un événement converge vers sa probabilité théorique :

$$ P(\text{Événement}) \approx \frac{\text{Nombre de fois où l'événement se produit}}{N} $$

### 2.6 Incertitude et Rigueur Statistique (Intervalles de Confiance)

Une estimation par Monte Carlo n'a de valeur scientifique absolue que si elle est assortie de son intervalle de confiance. Pour une probabilité empirique $p$ calculée sur $N$ simulations, l'erreur standard (SE) est :
$$ SE = \sqrt{\frac{p(1-p)}{N}} $$
L'intervalle de confiance à 95% est alors donné par $p \pm 1.96 \times SE$. 
Pour les événements extrêmement rares (ex: le Tadjikistan gagne la Coupe du Monde) où le simulateur renvoie $p = 0$, nous appliquons la **Règle de 3 de l'épidémiologie**. Même sans aucune occurrence sur 10 000 itérations, la vraie probabilité n'est pas strictement nulle ; l'intervalle de confiance supérieur mathématiquement prouvé est limité à $3 / N$ (soit $0.03\%$ pour $10\ 000$ itérations). Le Dashboard affiche scrupuleusement ces marges d'erreur.

---

## 3. Évaluation et Calibration du Modèle

Avant son déploiement "Live", le modèle a été formellement validé sur un large corpus historique via `model_backtest.py`. Deux métriques mathématiques ont été utilisées pour optimiser les paramètres $\text{base\_goals}$ et $\text{scale}$ :

1. **Log Loss (Perte Logarithmique croisée)** : 
   La Log Loss évalue la confiance de la prédiction et sanctionne lourdement les modèles arrogants qui se trompent.
   $$ \text{LogLoss} = -\frac{1}{M} \sum_{i=1}^{M} \log(P_{\text{true}, i}) $$
   Où $P_{\text{true}, i}$ est la probabilité que le modèle avait assigné au résultat qui s'est réellement produit.

2. **Brier Score (Erreur Quadratique Moyenne des probabilités)** :
   Le score de Brier (qui varie de 0 à 1) mesure la précision des probabilités assignées.
   $$ \text{Brier} = \frac{1}{M} \sum_{i=1}^{M} \sum_{c \in \{V_A, N, V_B\}} (P_{i, c} - O_{i, c})^2 $$
   Où $O_{i, c}$ vaut $1$ si le résultat s'est produit, $0$ sinon.

Les paramètres retenus sont ceux minimisant conjointement ces deux fonctions de coût, garantissant un modèle bien **calibré**, c'est-à-dire que lorsqu'il annonce $70\%$ de victoire, l'équipe gagne effectivement 7 fois sur 10 en moyenne historique.

---

## 4. Architecture Globale et Fichiers Clés

L'application repose sur une séparation stricte entre le moteur probabiliste, l'API et l'interface utilisateur.

### 4.1 La Data Pipeline (`src/data_acquisition/` et `scripts/`)
- Des scripts ETL téléchargent les bases de données Elo et les formats du tournoi (OpenFootball).
- `validate_data.py` assure l'intégrité de l'ensemble (équipes, stades, groupes) en validant strictement la donnée via Pydantic avant tout calcul.

### 4.2 Le Moteur (Backend Python)
- `poisson_model.py` et `simulate_tournament.py` constituent le cœur algorithmique.
- L'API FastAPI (`api/main.py`) expose l'état du tournoi, gère le "Admin Live" (saisie des scores) et pilote les exécutions de `run_monte_carlo.py` en tâche de fond.
- Le backend supporte également un endpoint "What-If" (`/api/what-if`) permettant d'estimer l'impact isolé d'un score fictif.

### 4.3 Le Tableau de Bord Interactif (Frontend React)
Développé avec React et l'écosystème web moderne, le Dashboard présente :
- Les **Prédictions** : Visualisation globale de l'arbre et des probabilités d'atteindre chaque stade.
- Les **Scores Live** : Affichage des matchs officiellement actés.
- L'**Admin Live** : Interface de modification d'état (injection des scores dans `real_results.json`).

---

## 5. Exploitation Dynamique : Deltas, What-If et Analyse Post-Tournoi

La véritable prouesse de ce système n'est pas la photographie statique pré-tournoi, mais le **Suivi de la Dérivée Probabiliste en Temps Réel**.

### 5.1 Suivi des Deltas (Tracker d'évolution)
À la fin de chaque journée du tournoi, l'opérateur (via "Admin Live") verrouille les résultats. L'API :
1. Met à jour les cotes Elo de la matrice en fonction des résultats réels.
2. Relance $N = 10,000$ itérations pour actualiser le reste du tournoi.
3. Crée un nouveau "Snapshot" des probabilités figées.

L'onglet **Deltas** calcule la différence entre la probabilité du Snapshot $T+1$ et du Snapshot $T$ pour isoler la valeur mathématique d'une victoire (ou d'une contre-performance).
$$ \Delta P = P(\text{Objectif})_{T+1} - P(\text{Objectif})_{T} $$

### 5.2 Scénarios d'Anticipation et God Mode (Chocs Elo)
Grâce au routeur d'administration et au système de "God Mode", le simulateur permet, avant même qu'un match ait lieu, d'injecter deux types de perturbations :
1. **Un score fictif (What-If)** : Anticiper un crash probabiliste dans l'arbre à élimination directe en forçant un résultat.
2. **Des Chocs Elo (God Mode)** : Ajouter ou retirer arbitrairement des points d'Elo à une équipe avant la simulation. Cela permet de quantifier mathématiquement l'impact d'événements stochastiques pré-tournoi (ex: blessure du joueur star de l'équipe, provoquant une perte estimée de 50 points d'Elo). L'algorithme se charge alors de recalculer le devenir entier de la compétition face à ce nouveau paradigme.

### 5.3 Analyse Scientifique Post-Compétition
À l'issue de la finale en juillet 2026, l'exhaustivité des logs générés par le simulateur (`outputs/snapshots/`) permettra une rétrospective statistique complète :
1. **Évaluation de la Calibration Réelle** : Calcul du Brier Score sur les 104 matchs de 2026. Le modèle Poisson indépendant est-il toujours pertinent face au football moderne ?
2. **Identification des Bascules et Cygnes Noirs** : Grâce à l'**Historique**, nous pourrons retracer l'instant "T" où les probabilités du Vainqueur Final ont explosé, ou diagnostiquer l'événement inattendu (Cygne Noir) qui a effondré le bracket théorique.
3. **Piste d'Amélioration (Comparaison de Modèles)** : L'utilitaire `model_comparison.py` permettra de jouer l'ensemble du tournoi *a posteriori* avec des modèles alternatifs (ex: Poisson Bivarié introduisant un facteur de corrélation de défense, ou intégration métrique Expected Goals - xG).

### 5.4 Perspectives Évolutives : Moteur "Intra-Match" (Live In-Game Updating)
Actuellement, l'architecture probabiliste du simulateur est discrète : les probabilités sont calculées entre les matchs. Une évolution conceptuelle majeure pour l'avenir serait de transformer le simulateur en un véritable moteur de type *bookmaker professionnel*, capable de recalculer les probabilités en continu **pendant** que le chronomètre du match tourne.

Cette évolution nécessiterait de remplacer l'espérance de buts statique ($\lambda$) par une fonction de survie dépendante du temps ($t$). La modélisation de base appliquerait une décroissance au paramètre de Poisson :
$$ \lambda_{live} = \lambda \times \left( \frac{90 - t}{90} \right) $$

Toutefois, pour refléter la dynamique complexe du football réel, cette fonction linéaire devra être enrichie par :
1. **L'Asymétrie de Fin de Match** : L'utilisation d'une distribution non-linéaire (ex: loi de Weibull) pour simuler la hausse drastique de probabilité de but dans les 15 dernières minutes due à la fatigue et au désespoir tactique.
2. **Le "Game State" (Score Actuel)** : La probabilité de marquer d'une équipe ($P_{marquer}$) diminue radicalement si elle mène au score (stratégie défensive), et augmente si elle est menée (stratégie ultra-offensive).
3. **Les Événements Discrets** : L'intégration en temps réel de chocs majeurs (cartons rouges, blessures, pénaltys) qui viennent modifier de manière instantanée et asymétrique les paramètres $\lambda_A$ et $\lambda_B$ avant d'appliquer la décroissance temporelle.

Ce chantier technique transformerait l'outil de simulation de tournoi en une plateforme de *Live Analytics* capable d'identifier au dixième de seconde près les anomalies de marché lors d'un match en direct.
