import pandas as pd
from django.core.management.base import BaseCommand
from apps.trust.models import ReviewScore

FEATURE_COLS = [
    'near_dup_score', 'is_burst_day', 'is_unverified', 'rating_deviation',
    'exclamation_count', 'word_count', 'avg_word_len',
    'positive_superlative_count', 'negative_superlative_count',
]


class Command(BaseCommand):
    help = (
        "Bootstrap: importe anomaly_scored_reviews.csv dans ReviewScore. "
        "Évite de relancer l'Isolation Forest pour les données historiques déjà scorées."
    )

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help="Chemin vers anomaly_scored_reviews.csv")

    def handle(self, *args, **opts):
        df = pd.read_csv(opts['csv_path'])
        created = 0
        skipped = 0

        for _, row in df.iterrows():
            defaults = {c: float(row[c]) for c in FEATURE_COLS}
            defaults['is_burst_day'] = bool(row['is_burst_day'])
            defaults['is_unverified'] = bool(row['is_unverified'])
            defaults['iso_prediction'] = int(row['iso_prediction'])
            defaults['iso_anomaly_score'] = float(row['iso_anomaly_score'])
            defaults['anomaly_frequency'] = float(row['anomaly_frequency']) if pd.notna(row['anomaly_frequency']) else None

            try:
                _, was_created = ReviewScore.objects.update_or_create(
                    review_id=row['reviewID'], defaults=defaults
                )
                created += int(was_created)
            except Exception as e:
                # ex: la review référencée n'existe pas encore -> importe cleaned_data.csv d'abord
                skipped += 1

        self.stdout.write(self.style.SUCCESS(f"{created} scores importés, {skipped} lignes ignorées (review inconnue)."))
