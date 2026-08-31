export type Review = {
  id: string;
  author: string;
  rating: number;
  date: string;
  title: string;
  body: string;
  verified: boolean;
  fakeScore: number; // 0-100, higher = more likely fake
};

export type Product = {
  asin: string;
  name: string;
  brand: string;
  rating: number;
  reviewCount: number;
  summary: string;
  pros: string[];
  cons: string[];
  ratingBreakdown: Record<1 | 2 | 3 | 4 | 5, number>;
  reviews: Review[];
};

const products: Product[] = [
  {
    asin: "B08N5WRWNW",
    name: "EchoLeaf Wireless Noise-Cancelling Headphones",
    brand: "EchoLeaf",
    rating: 4.3,
    reviewCount: 2841,
    summary:
      "Reviewers consistently praise the battery life (most report 30+ hours per charge) and the comfort of the memory-foam earcups during long sessions. Noise cancellation is described as strong for low-frequency noise like planes and trains, but less effective on voices. The most common complaint is the mobile app, which several buyers describe as buggy after firmware updates. A smaller group reports the plastic headband creaking after a few months of daily use.",
    pros: [
      "Battery life exceeds the advertised 30 hours for most buyers",
      "Comfortable for multi-hour wear",
      "Strong low-frequency noise cancellation",
    ],
    cons: [
      "Companion app is unreliable after updates",
      "Voices still audible with ANC on",
      "Occasional creaking in the headband",
    ],
    ratingBreakdown: { 5: 58, 4: 22, 3: 9, 2: 5, 1: 6 },
    reviews: [
      {
        id: "r1",
        author: "Marta L.",
        rating: 5,
        date: "2026-07-14",
        title: "Flew to Tokyo and never touched the charger",
        body: "Wore these for a 13-hour flight and still had over half the battery left. The engine drone basically disappears. Crying babies, less so, but it took the edge off.",
        verified: true,
        fakeScore: 4,
      },
      {
        id: "r2",
        author: "Dev P.",
        rating: 4,
        date: "2026-06-28",
        title: "Great sound, frustrating app",
        body: "Audio quality is genuinely excellent for the price and the EQ presets help. The app disconnected three times while I was trying to change settings after the last firmware update.",
        verified: true,
        fakeScore: 7,
      },
      {
        id: "r3",
        author: "Shopper2291",
        rating: 5,
        date: "2026-06-27",
        title: "BEST PRODUCT EVER!!! 5 STARS!!!",
        body: "Amazing product amazing quality amazing price I recommend to everyone buy now you will not regret it best headphones best seller fast shipping!!!",
        verified: false,
        fakeScore: 92,
      },
      {
        id: "r4",
        author: "Ellen R.",
        rating: 3,
        date: "2026-05-19",
        title: "Comfortable but the headband creaks",
        body: "Four months in and there's an audible creak every time I adjust them. Sound is still fine and the padding is soft, but I expected sturdier materials.",
        verified: true,
        fakeScore: 9,
      },
      {
        id: "r5",
        author: "Tomasz K.",
        rating: 5,
        date: "2026-04-30",
        title: "Replaced my much pricier pair",
        body: "I had a flagship set from a big brand and honestly prefer these for daily commuting. Pairing with two devices at once works reliably.",
        verified: true,
        fakeScore: 12,
      },
      {
        id: "r6",
        author: "A. Customer",
        rating: 5,
        date: "2026-04-29",
        title: "Perfect item, arrived fast",
        body: "Perfect item, arrived fast, works as described, very good seller, would buy again, five stars, thank you very much.",
        verified: false,
        fakeScore: 88,
      },
      {
        id: "r7",
        author: "Nadia B.",
        rating: 2,
        date: "2026-03-11",
        title: "Left cup died after five months",
        body: "The left earcup stopped producing sound. Support asked for a video and then went quiet for two weeks. Sound was good while it lasted.",
        verified: true,
        fakeScore: 15,
      },
      {
        id: "r8",
        author: "Greg H.",
        rating: 4,
        date: "2026-02-02",
        title: "Solid for calls",
        body: "Colleagues say I sound clear on calls even in a noisy cafe. Wish the case were slimmer for a backpack pocket.",
        verified: true,
        fakeScore: 6,
      },
    ],
  },
  {
    asin: "B07FZ8S74R",
    name: "TerraBrew Stainless Pour-Over Coffee Kettle",
    brand: "TerraBrew",
    rating: 4.6,
    reviewCount: 1163,
    summary:
      "Buyers highlight the precise gooseneck pour and how quickly the kettle reaches temperature, with many home baristas saying it improved their extraction consistency. The temperature dial is described as accurate within a couple of degrees. Recurring criticisms centre on the handle getting warm during long pours and a plastic smell during the first two or three uses that fades afterwards.",
    pros: [
      "Very controllable gooseneck flow",
      "Fast, accurate heating",
      "Sturdy stainless build",
    ],
    cons: ["Handle warms up on long pours", "Initial plastic odour", "Lid fits tightly"],
    ratingBreakdown: { 5: 68, 4: 20, 3: 6, 2: 3, 1: 3 },
    reviews: [
      {
        id: "k1",
        author: "Yusuf A.",
        rating: 5,
        date: "2026-08-02",
        title: "My pours finally look like the videos",
        body: "The spout gives you a thin, steady stream with almost no wrist effort. Blooming is far more even than with my old stovetop kettle.",
        verified: true,
        fakeScore: 5,
      },
      {
        id: "k2",
        author: "Priya S.",
        rating: 4,
        date: "2026-07-21",
        title: "Accurate thermometer, warm handle",
        body: "Checked it against a probe thermometer and it was within two degrees. The handle does get noticeably warm if you take a full minute to pour.",
        verified: true,
        fakeScore: 8,
      },
      {
        id: "k3",
        author: "DealHunter77",
        rating: 5,
        date: "2026-07-20",
        title: "Great great great",
        body: "Great kettle great price great shipping great seller great quality buy it now best on amazon!!!",
        verified: false,
        fakeScore: 90,
      },
      {
        id: "k4",
        author: "Lena F.",
        rating: 5,
        date: "2026-06-09",
        title: "Smell went away after two brews",
        body: "First fill had a faint plastic smell so I boiled and dumped twice. No issues since and it has become the piece of gear I use every morning.",
        verified: true,
        fakeScore: 11,
      },
      {
        id: "k5",
        author: "Omar D.",
        rating: 3,
        date: "2026-05-14",
        title: "Lid is a wrestling match",
        body: "Works well but the lid is so tight that I need a towel to get it off when hot. Otherwise no complaints about the pour.",
        verified: true,
        fakeScore: 10,
      },
      {
        id: "k6",
        author: "Hannah W.",
        rating: 5,
        date: "2026-03-25",
        title: "Doubles as a tea kettle",
        body: "The preset temperatures for green and black tea get used more than the coffee ones in our house. Keeps warm for a good half hour.",
        verified: true,
        fakeScore: 7,
      },
    ],
  },
];

export function getProduct(asin: string): Product | undefined {
  return products.find((p) => p.asin.toLowerCase() === asin.trim().toLowerCase());
}

export function listProducts(): Product[] {
  return products;
}

export function isValidAsin(value: string): boolean {
  return /^[A-Z0-9]{10}$/i.test(value.trim());
}
