# ml_artifacts/

Ce dossier doit contenir 3 fichiers, générés depuis `ml/notebooks/` (dossier `ml/`
au même niveau que `backend/`, pas dedans) :

- `tfidf.pkl`            -> depuis 02_Feature_Engineering.ipynb : `joblib.dump(tfidf, '../../backend/ml_artifacts/tfidf.pkl')`
- `scaler.pkl`           -> depuis 02_Feature_Engineering.ipynb : `joblib.dump(scaler, '../../backend/ml_artifacts/scaler.pkl')`
- `isolation_forest.pkl` -> depuis 03_Classic_ML.ipynb : `joblib.dump(iso, '../../backend/ml_artifacts/isolation_forest.pkl')`

Sans ces 3 fichiers, `python manage.py score_reviews` échouera avec un message clair
indiquant lequel manque.

Une fois générés, committe-les sur Git pour que toute l'équipe les ait sans avoir à
relancer les notebooks.
