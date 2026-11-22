import type { RecommendationItem } from "@/lib/types";

type RecommendationCardProps = {
  item: RecommendationItem;
};

function formatCost(value: number | null): string {
  if (value == null) return "N/A";
  return `₹${Math.round(value).toLocaleString("en-IN")} for two`;
}

function formatRating(value: number | null): string {
  if (value == null) return "N/A";
  return value.toFixed(1);
}

export function RecommendationCard({ item }: RecommendationCardProps) {
  const first = item.rank === 1;

  return (
    <article className="rounded-custom border border-border bg-card p-5 shadow-sm transition hover:border-border/90 sm:p-6">
      <div className="flex flex-col justify-between gap-2.5 pb-3 sm:flex-row sm:items-center">
        <div className="flex items-center gap-3">
          <span
            className={
              first
                ? "flex h-7 w-7 items-center justify-center rounded-lg bg-accent font-mono text-xs font-bold text-canvas shadow-sm"
                : "flex h-7 w-7 items-center justify-center rounded-lg border border-border bg-[#222222] font-mono text-xs font-bold text-text-primary"
            }
          >
            #{item.rank}
          </span>
          <h3 className="font-serif text-xl tracking-tight text-text-primary sm:text-2xl">
            {item.name || "Unknown restaurant"}
          </h3>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs text-text-muted">
          <span className="font-medium text-text-primary">
            {item.cuisine || "Cuisine N/A"}
          </span>
          <span className="text-border">·</span>
          <span className="inline-flex items-center gap-1 font-mono font-semibold text-accent">
            <svg className="h-3.5 w-3.5 fill-accent" viewBox="0 0 24 24" aria-hidden>
              <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
            </svg>
            {formatRating(item.rating)}
          </span>
          <span className="text-border">·</span>
          <span>{formatCost(item.estimated_cost)}</span>
          <span className="text-border">·</span>
          <span className="text-text-muted/90">
            {item.location || "Location N/A"}
          </span>
        </div>
      </div>
      <div className="border-t border-border/50 pt-3">
        <p className="line-clamp-2 text-sm leading-relaxed text-text-muted">
          <span className="mr-1.5 font-mono text-[11px] font-semibold uppercase tracking-wider text-accent">
            AI Fit:
          </span>
          {item.explanation || "No explanation available."}
        </p>
      </div>
    </article>
  );
}
