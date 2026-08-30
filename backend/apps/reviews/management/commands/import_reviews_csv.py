import pandas as pd
from django.core.management.base import BaseCommand
from apps.products.models import Product
from apps.reviews.models import Review


class Command(BaseCommand):
    help = "Bootstrap: importe cleaned_data.csv dans les tables Product + Review."

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help="Chemin vers cleaned_data.csv")

    def handle(self, *args, **opts):
        df = pd.read_csv(opts['csv_path'])
        df['at'] = pd.to_datetime(df['at'], errors='coerce')

        products_created = 0
        for asin in df['productASIN'].unique():
            _, created = Product.objects.get_or_create(asin=asin)
            products_created += int(created)

        reviews_created = 0
        for _, row in df.iterrows():
            _, created = Review.objects.update_or_create(
                review_id=row['reviewID'],
                defaults=dict(
                    product_id=row['productASIN'],
                    rating=row['rating'],
                    review_title=row.get('reviewTitle', '') or '',
                    review_url=row.get('reviewURL', '') or '',
                    review_position=row.get('reviewPosition'),
                    verified_purchase=bool(row['verifiedPurchase']),
                    helpful_vote_count=row.get('helpfulVoteCount', 0) or 0,
                    sentiment_score=row.get('sentiment_score'),
                    content_clean=row['content_clean'],
                    text_length=row.get('text_length'),
                    posted_at=row['at'] if pd.notna(row['at']) else None,
                )
            )
            reviews_created += int(created)

        self.stdout.write(self.style.SUCCESS(
            f"{products_created} produits créés, {reviews_created} reviews importées "
            f"({len(df)} lignes lues au total)."
        ))
