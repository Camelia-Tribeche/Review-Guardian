"""
Recalcule les 9 features utilisées par l'Isolation Forest (near_dup_score, is_burst_day, etc.)
pour les reviews d'UN SEUL produit à la fois — contrairement au notebook 02_Feature_Engineering
qui les calculait sur tout le dataset en une fois (impossible pour un backend qui reçoit
des reviews au fil de l'eau).

IMPORTANT : tfidf et scaler doivent être ceux DÉJÀ ENTRAÎNÉS (joblib.load), on ne fait
jamais de .fit() ici — seulement .transform() — sinon l'échelle des scores changerait
à chaque exécution et les scores ne seraient plus comparables entre eux dans le temps.
"""
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

FEATURE_COLS = [
    'near_dup_score', 'is_burst_day', 'is_unverified', 'rating_deviation',
    'exclamation_count', 'word_count', 'avg_word_len',
    'positive_superlative_count', 'negative_superlative_count',
]


def build_features(df: pd.DataFrame, tfidf, scaler) -> pd.DataFrame:
    """
    df attendu : colonnes review_id, content_clean, rating, verified_purchase, posted_at
                 (toutes les reviews d'UN SEUL productASIN)
    Retourne df + les 9 colonnes de FEATURE_COLS, déjà mises à l'échelle.
    """
    df = df.copy()
    df['posted_at'] = pd.to_datetime(df['posted_at'])

    # --- near_dup_score : review la plus proche mathématiquement dans CE produit ---
    X = tfidf.transform(df['content_clean'].fillna(''))
    n_neighbors = min(2, X.shape[0])
    if n_neighbors < 2:
        df['near_dup_score'] = 0.0
    else:
        nn = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine').fit(X)
        distances, _ = nn.kneighbors(X)
        df['near_dup_score'] = 1 - distances[:, -1]

    # --- is_burst_day : pic anormal de reviews un même jour, pour CE produit ---
    daily_counts = df.groupby(df['posted_at'].dt.date).size()
    mean_c = daily_counts.mean()
    std_c = daily_counts.std(ddof=0) or 0
    burst_dates = set(daily_counts[daily_counts > mean_c + 2 * std_c].index)
    df['is_burst_day'] = df['posted_at'].dt.date.isin(burst_dates).astype(int)

    # --- rating_deviation : écart à la moyenne des AUTRES reviews de CE produit (leave-one-out) ---
    n = len(df)
    if n > 1:
        total = df['rating'].sum()
        loo_mean = (total - df['rating']) / (n - 1)
        df['rating_deviation'] = (df['rating'] - loo_mean).abs()
    else:
        df['rating_deviation'] = 0.0

    df['is_unverified'] = (~df['verified_purchase'].astype(bool)).astype(int)
    df['word_count'] = df['content_clean'].str.split().apply(len)
    df['avg_word_len'] = df['content_clean'].apply(
        lambda t: np.mean([len(w) for w in str(t).split()]) if str(t).split() else 0
    )
    df['positive_superlative_count'] = df['content_clean'].str.count(
        r'\b(best|amazing|perfect|excellent|incredible)\b'
    )
    df['negative_superlative_count'] = df['content_clean'].str.count(
        r'\b(worst|terrible|awful|horrible)\b'
    )
    df['exclamation_count'] = df['content_clean'].str.count('!')

    df[FEATURE_COLS] = scaler.transform(df[FEATURE_COLS])
    return df
