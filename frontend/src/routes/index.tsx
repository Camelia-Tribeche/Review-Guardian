import { createFileRoute, Link } from "@tanstack/react-router";
import { ShieldAlert, Sparkles, ScanSearch, ThumbsUp, ArrowRight } from "lucide-react";
import { AsinSearch } from "@/components/AsinSearch";
import { SiteFooter, SiteHeader } from "@/components/SiteHeader";
import { StarRating } from "@/components/StarRating";
import { listProducts } from "@/lib/reviews-data";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Leafwise — AI Summaries for Amazon Reviews" },
      {
        name: "description",
        content:
          "Paste an Amazon ASIN to get an AI summary of the reviews, a rating breakdown, and fake-review detection.",
      },
      { property: "og:title", content: "Leafwise — AI Summaries for Amazon Reviews" },
      {
        property: "og:description",
        content:
          "Summarize thousands of Amazon reviews in seconds and see which ones look fake.",
      },
    ],
  }),
  component: Index,
});

const services = [
  {
    icon: Sparkles,
    title: "Review summaries",
    body: "We read every review on a listing and return one honest paragraph: what buyers love, what breaks, and what changed over time.",
  },
  {
    icon: ShieldAlert,
    title: "Fake review detection",
    body: "Each review gets an authenticity score from language patterns, timing bursts, reviewer history, and verified-purchase signals.",
  },
  {
    icon: ThumbsUp,
    title: "Pros and cons, ranked",
    body: "Recurring praise and complaints are clustered and ordered by how often real buyers mention them, not by star count.",
  },
  {
    icon: ScanSearch,
    title: "Rating you can trust",
    body: "We recompute the star average with suspicious reviews excluded, so you see the rating the listing actually earned.",
  },
];

const steps = [
  { n: "01", title: "Paste the ASIN", body: "Copy the 10-character code from the Amazon product page URL or its details table." },
  { n: "02", title: "We analyze the reviews", body: "Reviews are grouped by theme and scored for authenticity in a single pass." },
  { n: "03", title: "Read the verdict", body: "A summary, a clean rating, flagged reviews, and the full review list on one page." },
];

function Index() {
  const demos = listProducts();

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />

      <main className="flex-1">
        <section className="bg-leaf">
          <div className="mx-auto max-w-6xl px-5 py-16 md:py-24">
            <div>
              <span className="inline-flex items-center gap-2 rounded-full bg-primary-soft px-3 py-1 text-xs font-medium text-primary-deep">
                <Sparkles className="size-3.5" /> AI review intelligence
              </span>
              <h1 className="mt-5 text-4xl leading-tight font-semibold md:text-5xl">
                Know what buyers really think — before you buy
              </h1>
              <p className="mt-4 max-w-lg text-lg text-muted-foreground">
                Leafwise condenses thousands of Amazon reviews into one trustworthy summary and
                flags the reviews that look paid for.
              </p>
              <div id="search" className="mt-8 max-w-xl scroll-mt-24">
                <AsinSearch />
              </div>
            </div>
          </div>
        </section>

        <section id="services" className="scroll-mt-20 border-y border-border/70 bg-card">
          <div className="mx-auto max-w-6xl px-5 py-16 md:py-20">
            <h2 className="text-3xl font-semibold">What we do</h2>
            <p className="mt-3 max-w-2xl text-muted-foreground">
              Four services run on every listing you analyze — no settings, no configuration.
            </p>
            <div className="mt-10 grid gap-5 sm:grid-cols-2">
              {services.map((s) => (
                <article
                  key={s.title}
                  className="rounded-2xl border border-border bg-background p-6 transition-shadow hover:shadow-soft"
                >
                  <span className="flex size-11 items-center justify-center rounded-xl bg-primary-soft text-primary-deep">
                    <s.icon className="size-5" />
                  </span>
                  <h3 className="mt-4 text-lg font-semibold">{s.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{s.body}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section id="how" className="scroll-mt-20">
          <div className="mx-auto max-w-6xl px-5 py-16 md:py-20">
            <h2 className="text-3xl font-semibold">How it works</h2>
            <ol className="mt-10 grid gap-5 md:grid-cols-3">
              {steps.map((s) => (
                <li key={s.n} className="rounded-2xl bg-secondary/60 p-6">
                  <span className="font-display text-sm font-semibold text-primary-deep">{s.n}</span>
                  <h3 className="mt-2 text-lg font-semibold">{s.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{s.body}</p>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section className="border-t border-border/70 bg-card">
          <div className="mx-auto max-w-6xl px-5 py-16 md:py-20">
            <h2 className="text-3xl font-semibold">Try a sample listing</h2>
            <div className="mt-8 grid gap-5 sm:grid-cols-2">
              {demos.map((p) => (
                <Link
                  key={p.asin}
                  to="/product/$asin"
                  params={{ asin: p.asin }}
                  className="group rounded-2xl border border-border bg-background p-6 transition-shadow hover:shadow-soft"
                >
                  <p className="font-mono text-xs text-muted-foreground">{p.asin}</p>
                  <h3 className="mt-2 text-lg font-semibold group-hover:text-primary-deep">{p.name}</h3>
                  <div className="mt-3 flex items-center gap-2 text-sm text-muted-foreground">
                    <StarRating value={p.rating} />
                    {p.rating} · {p.reviewCount.toLocaleString()} reviews
                  </div>
                  <span className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-primary-deep">
                    View summary <ArrowRight className="size-4 transition-transform group-hover:translate-x-1" />
                  </span>
                </Link>
              ))}
            </div>
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
