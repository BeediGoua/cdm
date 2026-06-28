<!--
 Copyright 2026 gouab
 
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
 
     https://www.apache.org/licenses/LICENSE-2.0
 
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
-->

# Simulateur Coupe du Monde 2026 (CDM)

Un simulateur avancé de la Coupe du Monde 2026 basé sur des modèles statistiques (Dixon-Coles, Elo, classements FIFA) et des méthodes de Monte-Carlo. Le projet intègre un pipeline complet d'acquisition de données, de calibration de modèle, de backtesting, ainsi qu'une application Web Premium (FastAPI + React).

## 🚀 Prérequis

- Python 3.11 ou supérieur
- Node.js (pour l'application web)

## 🛠️ Installation et Configuration

1. **Créer et activer l'environnement virtuel :**
   ```bash
   python -m venv .venv
   
   # Windows (PowerShell) :
   .\.venv\Scripts\Activate.ps1
   
   # Linux/Mac (Bash) :
   source .venv/bin/activate
   ```

2. **Installer les dépendances Python :**
   ```bash
   pip install -r requirements.txt
   ```

## 📊 Acquisition et Préparation des Données

Avant d'exécuter des simulations, il est nécessaire de récupérer et valider les données de base :

```bash
# Lancer la pipeline d'acquisition (téléchargement, normalisation, import SQLite)
python src/data_acquisition/main.py

# Valider les données générées
python scripts/validate_data.py
```

## 🎲 Lancer une Simulation Monte-Carlo (CLI)

Pour exécuter une simulation de la Coupe du Monde (exemple avec 1500 itérations, modèle V3 Dixon-Coles) :

```bash
python -m src.domain.simulation.run_monte_carlo --n 1500 --mode pre_tournament --model-version V3
```
*Le résultat sera sauvegardé sous forme de snapshot dans `outputs/snapshots/`.*

## 🌐 Lancer l'Application Web (Interface Premium)

Le projet propose une interface utilisateur complète pour gérer les simulations et visualiser les résultats en temps réel.

1. **Lancer l'API Backend (FastAPI) :**
   Depuis la racine du projet, exécutez :
   ```bash
   uvicorn api.main:app --reload --port 8000
   ```

2. **Lancer le Front-End (React) :**
   Ouvrez un nouveau terminal, puis exécutez :
   ```bash
   cd web
   npm install
   npm run dev
   ```

3. **Accéder à l'application :**
   Ouvrez votre navigateur et allez sur [http://localhost:5173](http://localhost:5173).

## 🧹 Maintenance (Nettoyage des caches)

Si vous modifiez le code source, il est fortement recommandé de nettoyer les caches Python :

```powershell
# Windows (PowerShell) :
Get-ChildItem -Path . -Recurse -Force -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -Force -Filter '*.pyc' | Remove-Item -Force -ErrorAction SilentlyContinue
```
