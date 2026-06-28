# Priorité 1 : Validation des données existantes

## 1. Objectif
S'assurer que les données de base (fichiers JSON normalisés) sont complètes et cohérentes avant de commencer à construire les modèles de prédiction. 
Les fichiers concernés étaient :
- `teams.json`
- `groups.json`
- `groupMatches.json`
- `bracketRules.json`
- `venues.json`

## 2. Actions réalisées
J'ai créé un script Python de validation automatisé (`scripts/validate_data.py`) pour vérifier tous les critères clés listés dans le document `STEPS.md` :
1. Chaque équipe de `teams.json` possède bien un ID et une valeur Elo valide.
2. Tous les IDs d'équipes mentionnés dans les groupes (`groups.json`) ou les matchs (`groupMatches.json`) existent bien dans `teams.json`.
3. Le nombre total d'équipes attendues dans les groupes est bien de 48.
4. Tous les matchs possèdent bien le champ `matchday`.
5. Les options de qualification (`awaySlotOptions`) dans le `bracketRules.json` sont correctement formatées (ex: `["3A", "3B", ...]`).

## 3. Résultats et Corrections
Lors de la première exécution, le script a identifié **1 erreur** :
- **L'équipe d'Irlande (ID: `irl`)** ne possédait aucun rating Elo dans `teams.json`.

**Correction apportée :**
J'ai recherché les données de cette équipe dans les données brutes (`src/data/raw/footballratings_elo.csv`). J'ai pu confirmer que l'Irlande avait un score Elo de 1817 (rang 59). J'ai ensuite injecté manuellement ces valeurs dans le fichier `teams.json`.

Une fois la correction faite, la relance du script de validation a donné un résultat parfait : **0 erreur**.

## 4. Conclusion et Prochaines étapes
Les fondations de données sont désormais solides, complètes et validées. 
La priorité 1 est clôturée.

**Prochaine étape (Priorité 2)** :
Nous sommes prêts à passer à la création du moteur probabiliste. 
Il s'agira de développer le modèle Poisson (`src/domain/simulation/poisson_model.py`) avec les fonctions de base permettant de convertir les écarts Elo en moyennes de buts espérés ($\lambda$) et d'en déduire les probabilités de score.
