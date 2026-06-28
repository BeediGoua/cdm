# Priorité 2 : Modèle Poisson

## 1. Objectif
Construire le moteur mathématique qui permet de convertir la différence de niveau (Elo) entre deux équipes en prédictions probabilistes de scores de football.

## 2. Fichiers et Fonctions Créés
J'ai créé le fichier central du moteur de calcul :
`src/domain/simulation/poisson_model.py`

Ce fichier expose quatre fonctions principales :
1. **`compute_lambdas(elo_a, elo_b, base_goals, scale)`** :
   - **Comment ça marche :** Calcule l'écart Elo entre l'équipe A et l'équipe B, et utilise une fonction exponentielle pour ajuster la moyenne de buts (`base_goals`) attendue pour chaque équipe ($\lambda_A$ et $\lambda_B$).
   - **Pourquoi :** Le système Elo donne la force relative, mais un simulateur de matchs a besoin d'une espérance mathématique de buts.
2. **`poisson_pmf(k, lam)`** :
   - **Comment ça marche :** Implémente la formule mathématique de la loi de Poisson $P(X = k) = \frac{e^{-\lambda}\lambda^k}{k!}$.
   - **Pourquoi :** Permet de trouver la probabilité exacte qu'une équipe marque exactement $0, 1, 2, ... k$ buts en connaissant son espérance $\lambda$.
3. **`score_matrix(lambda_a, lambda_b)`** :
   - **Comment ça marche :** Croise les probabilités de buts des deux équipes pour créer une matrice 2D. Exemple : $P(A=2, B=1) = P(A=2) \times P(B=1)$.
   - **Pourquoi :** C'est indispensable pour modéliser tous les scores de matchs possibles (jusqu'à une limite raisonnable, fixée par défaut à 10 buts).
4. **`match_probabilities(lambda_a, lambda_b)`** :
   - **Comment ça marche :** Parcourt la matrice générée par `score_matrix` et somme les cases selon l'issue du match (Victoire A, Nul, ou Victoire B).
   - **Pourquoi :** Pour fournir une estimation globale claire des chances de chaque équipe, utile pour le contrôle et l'affichage.

## 3. Utilité du module
Ce fichier est le **"cerveau probabiliste"** du projet. Sans ce modèle, nous pourrions seulement dire "La France est meilleure que le Canada". Avec ce module, nous pouvons scientifiquement affirmer "La France a 60.1% de chances de gagner et devrait marquer en moyenne 1.92 buts contre 0.95 buts pour le Canada".

Il apporte :
- Une interprétation mathématique du rating Elo.
- La possibilité d'attribuer une vraie probabilité à chaque scénario.
- Le paramétrage (`scale` et `base_goals`) qui permettront plus tard de calibrer le modèle pour qu'il colle à l'historique réel des matchs internationaux.

## 4. Utilisation Future (Next Steps)
Le module `poisson_model.py` n'a pas vocation à être utilisé tout seul par l'utilisateur final. Il sera le "moteur caché" appelé par les couches supérieures :

- **Priorité 3 (simulate_match.py)** : Ce futur fichier va appeler `score_matrix` pour obtenir la distribution des scores, puis utilisera cette distribution pour tirer aléatoirement un score exact (mode "random"). C'est ce qui permettra d'ajouter du hasard contrôlé à chaque match.
- **Priorité 5 (run_monte_carlo.py)** : Le moteur Monte Carlo va faire appel indirectement au modèle Poisson pour simuler un tournoi entier 10 000 fois.
- **Priorité 7 (Calibration)** : Des scripts de calibration feront tourner ce modèle en boucle sur l'historique des matchs pour trouver les valeurs optimales de `scale` et `base_goals` afin de réduire la marge d'erreur (Log Loss).
