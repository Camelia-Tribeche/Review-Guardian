import { createFileRoute, Link } from "@tanstack/react-router";
import { AlertTriangle, ArrowLeft, BadgeCheck, ShieldCheck, Sparkles, ThumbsDown, ThumbsUp } from "lucide-react";
import { AsinSearch } from "@/components/AsinSearch";
import { SiteFooter, SiteHeader } from "@/components/SiteHeader";
import { StarRating } from "@/components/StarRating";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { getProduct, type Product, type Review } from "@/lib/reviews-data";

export const Route = createFileRoute("/product/$asin")({
  loader: ({ params }) => ({ product: getProduct(params.asin) ?? null, asin: params.asin }),
  head: ({ loaderData }) => {
    const name = loaderData?.product?.name;
    const title = name ? `${name} — Review summary | Leafwise` : "Product not found | Leafwise";
    const description = name
      ? `AI summary, trusted rating and fake-review analysis for ${name}.`
      : "We could not find review data for this ASIN.";
    return {
      meta: [
        { title },
        { name: "description", content: description },
        { property: "og:title", content: title },
        { property: "og:description", content: description },
        ...(name ? [] : [{ name: "robots", content: "noindex" }]),
      ],
    };
  },
  component: ProductPage,
});

function ProductPage() {
  const { product, asin } = Route.useLoaderData();

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="flex-1">
        {product ? <ProductDetail product={product} /> : <NotFound asin={asin} />}
      </main>
      <SiteFooter />
    </div>
  );
}

function NotFound({ asin }: { asin: string }) {
  return (
    <div className="mx-auto max-w-2xl px-5 py-20 text-center">
      <h1 className="text-3xl font-semibold">No review data for {asin}</h1>
      <p className="mt-3 text-muted-foreground">
        This demo ships with two analyzed listings. Try one of the sample ASINs below.
      </p>
      <div className="mt-8 text-left">
        <AsinSearch />
      </div>
    </div>
  );
}

function fakeVerdict(score: number) {
  if (score >= 70) return { label: "Likely fake", tone: "destructive" as const };
  if (score >= 40) return { label: "Suspicious", tone: "warning" as const };
  return { label: "Looks genuine", tone: "genuine" as const };
}

function ProductDetail({ product }: { product: Product }) {
  const flagged = product.reviews.filter((r) => r.fakeScore >= 70);
  const genuine = product.reviews.filter((r) => r.fakeScore < 70);
  const trustedRating =
    genuine.reduce((sum, r) => sum + r.rating, 0) / Math.max(genuine.length, 1);

  return (
    <>
      <section className="bg-leaf">
        <div className="mx-auto max-w-6xl px-5 py-10">
          <Link to="/" className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-primary-deep">
            <ArrowLeft className="size-4" /> Analyze another product
          </Link>
          <p className="mt-6 font-mono text-xs text-muted-foreground">ASIN {product.asin}</p>
          <h1 className="mt-2 max-w-3xl text-3xl font-semibold md:text-4xl">{product.name}</h1>
          <p className="mt-2 text-muted-foreground">by {product.brand}</p>

          <div className="mt-6 flex flex-wrap items-center gap-6">
            <div>
              <div className="flex items-center gap-2">
                <span className="font-display text-3xl font-semibold">{product.rating.toFixed(1)}</span>
                <StarRating value={product.rating} size={18} />
              </div>
              <p className="text-sm text-muted-foreground">
                Listed average · {product.reviewCount.toLocaleString()} reviews
              </p>
            </div>
            <div className="rounded-xl bg-card px-4 py-3 shadow-soft">
              <div className="flex items-center gap-2">
                <ShieldCheck className="size-4 text-primary" />
                <span className="font-display text-2xl font-semibold">{trustedRating.toFixed(1)}</span>
                <StarRating value={trustedRating} size={16} />
              </div>
              <p className="text-sm text-muted-foreground">Leafwise rating, suspicious reviews removed</p>
            </div>
          </div>
        </div>
      </section>

      <div className="mx-auto grid max-w-6xl gap-8 px-5 py-12 lg:grid-cols-[1.6fr_1fr]">
        <div className="space-y-8">
          <article className="rounded-2xl border border-border bg-card p-6 shadow-soft">
            <h2 className="flex items-center gap-2 text-xl font-semibold">
              <Sparkles className="size-5 text-primary" /> AI review summary
            </h2>
            <p className="mt-4 leading-relaxed text-foreground/90">{product.summary}</p>

            <div className="mt-6 grid gap-5 sm:grid-cols-2">
              <div className="rounded-xl bg-primary-soft/60 p-4">
                <h3 className="flex items-center gap-2 text-sm font-semibold text-primary-deep">
                  <ThumbsUp className="size-4" /> What buyers praise
                </h3>
                <ul className="mt-3 space-y-2 text-sm text-foreground/90">
                  {product.pros.map((p) => (
                    <li key={p} className="flex gap-2">
                      <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-primary" />
                      {p}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="rounded-xl bg-muted p-4">
                <h3 className="flex items-center gap-2 text-sm font-semibold">
                  <ThumbsDown className="size-4" /> Recurring complaints
                </h3>
                <ul className="mt-3 space-y-2 text-sm text-foreground/90">
                  {product.cons.map((c) => (
                    <li key={c} className="flex gap-2">
                      <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-muted-foreground" />
                      {c}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </article>

          <section>
            <h2 className="text-xl font-semibold">
              Reviews <span className="text-muted-foreground">({product.reviews.length} analyzed)</span>
            </h2>
            <ul className="mt-5 space-y-4">
              {product.reviews.map((review) => (
                <li key={review.id}>
                  <ReviewCard review={review} />
                </li>
              ))}
            </ul>
          </section>
        </div>

        <aside className="space-y-6">
          <section className="rounded-2xl border border-border bg-card p-6">
            <h2 className="text-lg font-semibold">Rating breakdown</h2>
            <ul className="mt-4 space-y-3">
              {([5, 4, 3, 2, 1] as const).map((stars) => (
                <li key={stars} className="flex items-center gap-3 text-sm">
                  <span className="w-10 shrink-0 text-muted-foreground">{stars} ★</span>
                  <Progress value={product.ratingBreakdown[stars]} className="h-2" />
                  <span className="w-9 shrink-0 text-right text-muted-foreground">
                    {product.ratingBreakdown[stars]}%
                  </span>
                </li>
              ))}
            </ul>
          </section>

          <section className="rounded-2xl border border-border bg-card p-6">
            <h2 className="flex items-center gap-2 text-lg font-semibold">
              <AlertTriangle className="size-5 text-warning" /> Fake review check
            </h2>
            <p className="mt-3 text-sm text-muted-foreground">
              {flagged.length} of {product.reviews.length} analyzed reviews show patterns typical of
              incentivized or generated text.
            </p>
            <div className="mt-4 rounded-xl bg-muted p-4">
              <p className="font-display text-3xl font-semibold">
                {Math.round((flagged.length / product.reviews.length) * 100)}%
              </p>
              <p className="text-sm text-muted-foreground">flagged as likely fake</p>
            </div>
            <ul className="mt-4 space-y-2 text-sm text-muted-foreground">
              <li>· Repetitive superlatives with no product detail</li>
              <li>· Clusters of same-day five-star posts</li>
              <li>· Missing verified-purchase confirmation</li>
            </ul>
          </section>
        </aside>
      </div>
    </>
  );
}

function ReviewCard({ review }: { review: Review }) {
  const verdict = fakeVerdict(review.fakeScore);

  return (
    <article className="rounded-2xl border border-border bg-card p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="flex size-9 items-center justify-center rounded-full bg-primary-soft text-sm font-semibold text-primary-deep">
            {review.author.charAt(0)}
          </span>
          <div>
            <p className="text-sm font-medium">{review.author}</p>
            <p className="text-xs text-muted-foreground">
              {new Date(review.date).toLocaleDateString("en-GB", {
                day: "numeric",
                month: "short",
                year: "numeric",
              })}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {review.verified && (
            <Badge variant="secondary" className="gap-1">
              <BadgeCheck className="size-3.5" /> Verified purchase
            </Badge>
          )}
          <Badge
            variant={verdict.tone === "destructive" ? "destructive" : "outline"}
            className={
              verdict.tone === "warning"
                ? "border-warning text-warning-foreground"
                : verdict.tone === "genuine"
                  ? "border-primary text-primary-deep"
                  : undefined
            }
          >
            {verdict.label} · {review.fakeScore}
          </Badge>
        </div>
      </div>

      <div className="mt-4 flex items-center gap-2">
        <StarRating value={review.rating} />
        <h3 className="text-sm font-semibold">{review.title}</h3>
      </div>
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{review.body}</p>
    </article>
  );
}
