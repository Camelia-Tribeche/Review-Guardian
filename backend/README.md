# Backend Django — Détection de faux avis Amazon

## Structure du projet

`ml/` et `backend/` sont au même niveau (siblings), pas l'un dans l'autre :

```
Review--Guardian/
├── ml/
│   ├── data/
│   │   ├── raw/            (reviews.csv — donnée brute avant nettoyage)
│   │   └── processed/      (cleaned_data.csv, featured_reviews.csv, anomaly_scored_reviews.csv)
│   ├── notebooks/
│   └── src/
└── backend/
    ├── apps/
    ├── config/
    ├── ml_artifacts/       <- les .pkl générés par les notebooks vont ICI
    ├── venv/
    ├── manage.py
    └── requirements.txt
```

## Installation

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# édite .env avec tes identifiants MySQL
```

```sql
CREATE DATABASE reviews_trust_db CHARACTER SET utf8mb4;
```

## Étape 1 — Créer les tables

```bash
python manage.py makemigrations products reviews trust
python manage.py migrate
python manage.py createsuperuser
```

## Étape 2 — Générer les artefacts ML (OBLIGATOIRE avant score_reviews)

Dans `ml/notebooks/02_Feature_Engineering.ipynb`, juste après les cellules qui créent
`tfidf` et `scaler`, ajoute :

```python
import joblib
joblib.dump(tfidf, '../../backend/ml_artifacts/tfidf.pkl')
joblib.dump(scaler, '../../backend/ml_artifacts/scaler.pkl')
```

Dans `ml/notebooks/03_Classic_ML.ipynb`, juste après `iso.fit(X)`, ajoute :

```python
joblib.dump(iso, '../../backend/ml_artifacts/isolation_forest.pkl')
```

(`../..` depuis `ml/notebooks/` remonte à la racine `Review--Guardian/`, puis on redescend
dans `backend/ml_artifacts/`.)

Puis **Kernel > Restart & Run All** sur les deux notebooks (pas juste la nouvelle
cellule — sinon `tfidf`/`scaler`/`iso` n'existent pas encore en mémoire, voir notre
discussion plus haut sur pourquoi).

Vérifie ensuite : `ls backend/ml_artifacts/` doit afficher `tfidf.pkl`, `scaler.pkl`,
`isolation_forest.pkl`.

## Étape 3 — Bootstrap avec tes données existantes

```bash
python manage.py import_reviews_csv ../ml/data/processed/cleaned_data.csv
python manage.py import_review_scores_csv ../ml/data/processed/anomaly_scored_reviews.csv
```

(`ml/data/raw/reviews.csv` et `ml/data/processed/featured_reviews.csv` ne sont pas utilisés
par le backend — le premier est la donnée brute avant nettoyage, le second est une étape
intermédiaire déjà incluse dans `anomaly_scored_reviews.csv`.)

## Étape 4 — Générer les résumés IA (lent, tourne sur CPU)

```bash
python manage.py generate_summaries
```

## Étape 5 — Lancer le serveur

```bash
python manage.py runserver
```

## Ajouter de nouvelles reviews plus tard

1. Ajoute-les via `/admin/` (Reviews > Add Review) ou un script d'import.
2. `python manage.py score_reviews` (ne traite que les nouvelles, par défaut).
3. `python manage.py generate_summaries` (régénère le résumé du produit concerné).

## Endpoints API

| Méthode | URL | Description |
|---|---|---|
| GET | `/api/products/` | Liste des produits + rapport de confiance |
| GET | `/api/products/{asin}/` | Détail d'un produit |
| GET | `/api/products/{asin}/reviews/` | Reviews du produit, avec score de confiance |
| GET | `/admin/` | Interface d'administration Django |
