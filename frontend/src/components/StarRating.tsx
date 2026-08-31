import { Star } from "lucide-react";
import { cn } from "@/lib/utils";

export function StarRating({
  value,
  size = 16,
  className,
}: {
  value: number;
  size?: number;
  className?: string;
}) {
  return (
    <span className={cn("inline-flex items-center gap-0.5", className)} aria-label={`${value} out of 5 stars`}>
      {[1, 2, 3, 4, 5].map((i) => {
        const filled = value >= i - 0.25;
        const half = !filled && value >= i - 0.75;
        return (
          <Star
            key={i}
            width={size}
            height={size}
            strokeWidth={1.5}
            className={cn(
              "shrink-0",
              filled ? "fill-star text-star" : half ? "fill-star/50 text-star" : "fill-transparent text-muted-foreground/50",
            )}
          />
        );
      })}
    </span>
  );
}
