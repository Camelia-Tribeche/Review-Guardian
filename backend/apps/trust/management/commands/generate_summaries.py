from django.core.management.base import BaseCommand
from django.db.models import Avg

from apps.products.models import Product
from apps.trust.models import ProductTrustReport
from apps.trust.services.pi_defense import verify_summary_safety
from apps.trust.services.summarizer import (
    chunk_reviews, summarize_chunk, reformat_to_structured,
    merge_summaries, parse_structured_summary,
)


class Command(BaseCommand):
    help = (
        "Génère le résumé PROS/CONS/VERDICT par produit, à partir des reviews jugées "
        "de confiance (iso_prediction=1). Lourd -- à lancer en tâche batch/cron, "
        "jamais dans une requête HTTP."
    )

    def add_arguments(self, parser):
        parser.add_argument('--product', help="Ne traiter qu'un seul productASIN")

    def handle(self, *args, **opts):
        products = Product.objects.all()
        if opts.get('product'):
            products = products.filter(asin=opts['product'])

        for product in products:
            all_reviews = product.reviews.all()
            total = all_reviews.count()
            if total == 0:
                continue

            trusted_reviews = all_reviews.filter(score__iso_prediction=1)
            fake_count = total - trusted_reviews.count()
            if not trusted_reviews.exists():
                self.stdout.write(f"[{product.asin}] aucune review de confiance, résumé ignoré.")
                continue

            texts = list(trusted_reviews.values_list('content_clean', flat=True))
            chunks = chunk_reviews(texts, chunk_size=40)

            self.stdout.write(f"[{product.asin}] {len(chunks)} chunk(s) à résumer...")
            chunk_summaries = [summarize_chunk(c) for c in chunks]
            structured = [reformat_to_structured(s) for s in chunk_summaries]
            final_raw = merge_summaries(structured)
            final_safe, _ = verify_summary_safety(final_raw)
            parsed = parse_structured_summary(final_safe)

            raw_avg = all_reviews.aggregate(avg=Avg('rating'))['avg'] or 0
            adjusted_avg = trusted_reviews.aggregate(avg=Avg('rating'))['avg'] or raw_avg

            ProductTrustReport.objects.update_or_create(
                product=product,
                defaults=dict(
                    total_reviews=total,
                    fake_count=fake_count,
                    authenticity_rate=(total - fake_count) / total * 100,
                    raw_avg_rating=round(raw_avg, 2),
                    adjusted_rating=round(adjusted_avg, 2),
                    summary_text=final_safe,
                    pros=parsed['pros'],
                    cons=parsed['cons'],
                    verdict=parsed['verdict'],
                )
            )
            self.stdout.write(self.style.SUCCESS(f"[{product.asin}] résumé généré."))
