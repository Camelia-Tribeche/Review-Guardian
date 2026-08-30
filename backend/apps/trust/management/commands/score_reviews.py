import joblib
import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.reviews.models import Review
from apps.trust.models import ReviewScore
from apps.trust.services.feature_engineering import build_features, FEATURE_COLS


class Command(BaseCommand):
    help = (
        "Calcule le ReviewScore (features + Isolation Forest) pour les reviews qui n'en ont "
        "pas encore -- typiquement, les reviews ajoutées manuellement depuis le dernier passage. "
        "Utilise --all pour tout recalculer."
    )

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true', help="Recalcule aussi les reviews déjà scorées")
        parser.add_argument('--product', help="Ne traiter qu'un seul productASIN")

    def handle(self, *args, **opts):
        artifacts_dir = settings.ML_ARTIFACTS_DIR
        try:
            tfidf = joblib.load(artifacts_dir / 'tfidf.pkl')
            scaler = joblib.load(artifacts_dir / 'scaler.pkl')
            iso = joblib.load(artifacts_dir / 'isolation_forest.pkl')
        except FileNotFoundError as e:
            raise CommandError(
                f"Artefact manquant dans {artifacts_dir} ({e}). "
                "Il faut d'abord sauvegarder tfidf.pkl / scaler.pkl / isolation_forest.pkl "
                "depuis les notebooks 02 et 03 (voir joblib.dump)."
            )

        asins = Review.objects.values_list('product_id', flat=True).distinct()
        if opts.get('product'):
            asins = asins.filter(product_id=opts['product']) if hasattr(asins, 'filter') else [opts['product']]

        total_scored = 0
        for asin in asins:
            product_reviews = Review.objects.filter(product_id=asin)
            to_score = product_reviews if opts['all'] else product_reviews.filter(score__isnull=True)
            if not to_score.exists():
                continue

            # near_dup / burst / rating_deviation ont besoin du CONTEXTE de tout le produit,
            # même les reviews déjà scorées -> on recharge tout, mais on ne sauvegarde que
            # les reviews réellement ciblées par le filtre ci-dessus.
            df = pd.DataFrame(list(product_reviews.values(
                'review_id', 'content_clean', 'rating', 'verified_purchase', 'posted_at'
            )))
            features_df = build_features(df, tfidf, scaler)
            X = features_df[FEATURE_COLS]
            features_df['iso_prediction'] = iso.predict(X)
            features_df['iso_anomaly_score'] = iso.decision_function(X)

            target_ids = set(to_score.values_list('review_id', flat=True))
            subset = features_df[features_df['review_id'].isin(target_ids)]
            for _, row in subset.iterrows():
                defaults = row[FEATURE_COLS + ['iso_prediction', 'iso_anomaly_score']].to_dict()
                defaults['is_burst_day'] = bool(defaults['is_burst_day'])
                defaults['is_unverified'] = bool(defaults['is_unverified'])
                defaults['iso_prediction'] = int(defaults['iso_prediction'])
                ReviewScore.objects.update_or_create(review_id=row['review_id'], defaults=defaults)
                total_scored += 1

        self.stdout.write(self.style.SUCCESS(f"{total_scored} reviews scorées."))
