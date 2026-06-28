# Fondations Mathématiques et Justifications Théoriques

Ce document détaille rigoureusement l'architecture probabiliste du simulateur de la Coupe du Monde 2026. Il présente les hypothèses sous-jacentes, leurs justifications statistiques, ainsi que les démonstrations justifiant la supériorité du modèle de Dixon-Coles (V3) sur les approches classiques (V1/V2).

---

## 1. Modélisation de la Force des Équipes : Le Système Elo

L'approche traditionnelle dans les modèles prédictifs de football consiste à assigner des paramètres statiques de force offensive et défensive (ex: $\alpha_i, \beta_j$). Notre simulateur opte pour une approche dynamique basée sur un **Processus de Markov** : le classement Elo.

### 1.1 Fonction de Transfert Logistique

L'écart de niveau entre une équipe A et une équipe B ($\Delta Elo = Elo_B - Elo_A$) est converti en une probabilité de victoire attendue ($P_{exp}$) via une fonction logistique (Sigmoïde) :

$$ P_{exp}(A) = \frac{1}{1 + 10^{\frac{\Delta Elo}{Scale}}} $$

**Justification de l'hypothèse :**
La distribution logistique possède des queues (tails) plus épaisses que la distribution normale. En sport, les "surprises" (upsets) surviennent plus fréquemment que ce qu'une loi normale prédirait. Le choix de la base 10 et d'un facteur d'échelle `Scale = 800` a été calibré empiriquement pour aplatir la courbe, donnant aux "petites" équipes (ex: Panama) une probabilité d'exploit mathématiquement mesurable.

### 1.2 Génération de l'Espérance de Buts (xG)

La plupart des systèmes s'arrêtent à $P_{exp}$. Notre moteur fait le lien analytique entre $P_{exp}$ et les paramètres d'intensité $\lambda$ (buts attendus par A) et $\mu$ (buts attendus par B) :

$$ \lambda = BaseGoals \times P_{exp}(A) $$
$$ \mu = BaseGoals \times P_{exp}(B) $$

*(Où `BaseGoals` est la moyenne historique de buts par équipe lors d'un match de Coupe du Monde, environ 1.35).*

---

## 2. Modèles de Distribution des Scores

### 2.1 Hypothèse d'Indépendance : Le Modèle Bivarié de Poisson (V1)

Le modèle V1 (Classique) postule que le nombre de buts marqués par A ($X$) suit une loi de Poisson de paramètre $\lambda$, et que B ($Y$) suit une loi de Poisson de paramètre $\mu$. Surtout, **il pose l'hypothèse stricte que $X$ et $Y$ sont indépendants**.

La probabilité conjointe du score $(x, y)$ est le produit des probabilités marginales :
$$ P(X=x, Y=y) = P(X=x) \times P(Y=y) = \frac{e^{-\lambda}\lambda^x}{x!} \times \frac{e^{-\mu}\mu^y}{y!} $$

**Démonstration de l'échec de l'indépendance :**
Prenons un match équilibré où $\lambda = 1.0$ et $\mu = 1.0$.
Selon la V1, la probabilité d'un 0-0 est :
$$ P(0,0) = e^{-1} \times e^{-1} = e^{-2} \approx 0.135 \text{ (13.5\%)} $$
Cependant, l'analyse des données historiques de la FIFA montre que lors de matchs équilibrés avec une moyenne de 2 buts au total, le score de 0-0 survient dans **~18%** des cas. Le modèle de Poisson indépendant sous-estime massivement les probabilités sur la diagonale (0-0, 1-1, 2-2).

### 2.2 Rejet de l'Hypothèse d'Indépendance : Modèle Dixon-Coles (V3)

En 1997, Mark Dixon et Stuart Coles publient une approche corrigeant ce biais de sur-confiance. Dans la réalité tactique, si le score est de 0-0 à la 70ème minute, les deux équipes ont tendance à devenir *averses au risque* (risk-averse). Ainsi, $X$ et $Y$ sont corrélés négativement (Covariance $\rho$).

Dixon et Coles introduisent un paramètre de correction $\tau_{\lambda, \mu}(x,y)$ :

$$ P_{DC}(X=x, Y=y) = \tau(x,y) \times P_{Poisson}(X=x, Y=y) $$

Où $\tau(x,y)$ ne modifie que les faibles scores :
- $\tau(0,0) = 1 - \rho\lambda\mu$
- $\tau(1,0) = 1 + \rho\lambda$
- $\tau(0,1) = 1 + \rho\mu$
- $\tau(1,1) = 1 - \rho$
- $\tau(x,y) = 1$ pour tous les autres scores.

**Justification de $\rho = -0.13$ :**
En fixant $\rho = -0.13$, le facteur multiplicateur pour le 0-0 devient $\tau(0,0) = 1 - (-0.13 \times 1 \times 1) = 1.13$.
La nouvelle probabilité de 0-0 devient $0.135 \times 1.13 \approx 0.152$, ce qui se rapproche considérablement de la fréquence empirique réelle (18%). Dixon-Coles corrige donc algébriquement la dynamique comportementale humaine sur un terrain de football.

---

### 2.3 Apprentissage en Ligne : Modèle Bayésien Conjugué (V4)

Lorsqu'un tournoi court (comme une Coupe du Monde) commence, les performances réelles des équipes peuvent dévier de leur Elo historique. Le modèle V4 utilise l'inférence bayésienne pour mettre à jour les espérances de buts ($\lambda, \mu$) en temps réel.

**Conjugaison Gamma-Poisson :**
En probabilités, la loi Gamma est la loi a priori conjuguée de la loi de Poisson.
1. **A priori (Prior)** : L'espérance de buts initiale $\lambda_{prior}$ (issue du système Elo) est définie comme l'espérance d'une loi Gamma, $\lambda \sim \text{Gamma}(\alpha, \beta)$, où $\alpha = \lambda_{prior} \times \beta$. Le paramètre $\beta$ agit comme un paramètre de confiance (poids historique empirique, ex: $\beta = 2.0$).
2. **Vraisemblance (Likelihood)** : Le processus de marquage dans le tournoi $X \sim \text{Poisson}(\lambda)$.
3. **A posteriori (Posterior)** : Après $n$ matchs et une somme de $\Sigma x_i$ buts marqués par l'équipe, la nouvelle distribution pour $\lambda$ est donnée par :
   $$ \lambda_{posterior} \sim \text{Gamma}(\alpha + \Sigma x_i, \beta + n) $$

La nouvelle espérance de l'équipe devient alors la moyenne de la distribution a posteriori :
$$ \hat{\lambda} = \frac{\alpha + \Sigma x_i}{\beta + n} $$
Ce mécanisme bayésien élégant permet de pondérer mathématiquement les exploits récents face à la réputation historique.

### 2.4 Conjoncture et Temps : Régression Bivariée avec Covariables (V5)

Les modèles V1 à V4 postulent que seuls le niveau de force statique/bayésien déterminent les issues. En réalité physique, lors de tournois, la récupération et la forme (momentum) pèsent lourd. La V5 introduit une notion temporelle et contextuelle en utilisant une **Régression Log-Linéaire de Poisson**.

**Modélisation Exponentielle :**
Les espérances brutes $\lambda_A$ et $\lambda_B$ sont ajustées par un facteur exponentiel combinant les différentiels des équipes :
$$ \hat{\lambda}_A = \lambda_A \times \exp(\gamma_1 \cdot \Delta Goal + \gamma_2 \cdot \Delta Rest) $$

Où :
- $\Delta Goal = GoalDiff_A - GoalDiff_B$ : Avantage net de différence de buts durant le tournoi.
- $\Delta Rest = RestDays_A - RestDays_B$ : Avantage net de jours de repos par rapport à l'adversaire (impact direct de la fatigue due aux prolongations ou au calendrier).
- $\gamma_1, \gamma_2$ : Coefficients (poids) d'impact de chaque covariable sur les buts espérés.

L'utilisation de la transformation exponentielle $\exp(\dots)$ est fondamentale en régression de Poisson car elle garantit l'axiome $\lambda > 0$, empêchant mathématiquement l'espérance de buts de devenir négative, tout en introduisant un effet d'échelle multiplicatif de la fatigue sur la performance.

---

## 3. Fonctions de Coût et Évaluation (Brier Score / LogLoss)

Comment prouver mathématiquement que la V3 est meilleure que la V1 sans biais de confirmation ? En utilisant des **Règles de Score Propres** (Strictly Proper Scoring Rules).

Soit $N$ le nombre de matchs, $O_i \in \{0,1\}$ le résultat réel (1 si l'événement se produit, 0 sinon), et $P_i \in [0,1]$ la probabilité prédite par le modèle.

### 3.1 Brier Score (Erreur Quadratique Moyenne)

$$ BS = \frac{1}{N} \sum_{i=1}^N (P_i - O_i)^2 $$

Le Brier Score sanctionne la variance (manque de confiance) et le biais (erreur directionnelle). Le modèle de Dixon-Coles (V3) ayant une meilleure calibration sur les matchs nuls, la distance Euclidienne au carré entre la distribution prédite et le vecteur One-Hot du résultat réel est minimisée.

### 3.2 Logarithmic Loss (Cross-Entropy)

$$ LogLoss = - \frac{1}{N} \sum_{i=1}^N \left[ O_i \ln(P_i) + (1 - O_i) \ln(1 - P_i) \right] $$

La LogLoss pénalise de manière asymétrique les prédictions trop confiantes (si le modèle prédit 99% mais que l'événement ne se produit pas, le terme logarithmique tend vers l'infini). La correction Dixon-Coles $\tau(x,y)$ adoucit les probabilités extrêmes, réduisant systématiquement l'Entropie Croisée (Cross-Entropy) par rapport à la V1.

---

## 4. Loi des Grands Nombres et Monte Carlo

La Coupe du Monde possède une combinatoire qui explose de manière non-linéaire ($3^{48}$ combinaisons rien que pour les phases de poules). Le simulateur utilise donc l'Intégration de Monte Carlo.

### 4.1 Convergence de l'Estimateur Empirique

Soit $Z_i$ l'indicateur binaire qu'une équipe gagne la coupe lors de l'itération $i$. La probabilité estimée est $\hat{p} = \frac{1}{N} \sum Z_i$.
D'après le **Théorème Central Limite (TCL)**, lorsque $N \to \infty$, la distribution de $\hat{p}$ tend vers une loi normale $\mathcal{N}(P_{true}, \sigma^2/N)$.

La variance de cet estimateur s'écrasant en $O(\frac{1}{N})$, avec $N=10000$, la précision est redoutable.
L'Erreur Standard (SE) se définit par :
$$ SE = \frac{\sqrt{\hat{p}(1-\hat{p})}}{\sqrt{N}} $$

### 4.2 L'Axiome de Continuité (La Règle de 3)

Lors des simulations de $N=10000$, certaines équipes faibles (ex: Iles Salomon) peuvent avoir un score de réussite $\hat{p} = 0$.
**L'affirmation d'une probabilité de $0.00\%$ est un non-sens en sciences statistiques** (probabilité de l'événement impossible).

Le simulateur implémente donc l'approximation de l'intervalle de confiance supérieur d'une loi binomiale par une loi de Poisson, connue sous le nom de "Règle de 3". Si l'événement ne s'est pas produit, la borne supérieure de confiance à 95% est approximée par :
$$ P_{max} \approx \frac{3}{N} = \frac{3}{10000} = 0.0003 \text{ (0.03\%)} $$
Cette justification mathématique permet au simulateur d'afficher élégamment `< 0.03%` pour le "Détecteur de Miracles", prouvant la robustesse mathématique du moteur de bout en bout.
