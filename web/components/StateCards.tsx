import type { UiError } from "@/lib/types";

export function LoadingCard({ restaurantCount }: { restaurantCount: number }) {
  return (
    <section className="space-y-4 rounded-custom border border-border bg-card p-8 text-center">
      <div className="mx-auto inline-flex h-12 w-12 items-center justify-center rounded-full border border-accent/25 bg-accent/10 text-accent animate-pulseSoft">
        ↻
      </div>
      <div className="mx-auto max-w-md space-y-1">
        <p className="font-serif text-lg text-text-primary sm:text-xl">
          Finding matches and asking the AI to rank them…
        </p>
        <p className="text-xs text-text-muted">
          Filtering {restaurantCount.toLocaleString()} restaurant listings against
          your budget & rating constraints.
        </p>
      </div>
    </section>
  );
}

export function EmptyCard({ message }: { message?: string | null }) {
  return (
    <section className="space-y-4 rounded-custom border border-border bg-card p-8 text-center sm:p-10">
      <div className="mx-auto inline-flex h-12 w-12 items-center justify-center rounded-full border border-warning-border bg-warning-bg text-lg font-bold text-warning">
        !
      </div>
      <div className="mx-auto max-w-lg space-y-2">
        <h3 className="font-serif text-xl text-text-primary">
          {message || "No restaurants matched these filters."}
        </h3>
        <p className="text-sm leading-relaxed text-text-muted">
          Try a broader location, different cuisine, lower min rating, or another
          budget.
        </p>
      </div>
    </section>
  );
}

export function ErrorCard({ error }: { error: UiError }) {
  return (
    <section className="space-y-4 rounded-custom border border-border bg-card p-8 sm:p-10">
      <div className="flex items-start gap-4">
        <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-custom border border-error-border bg-error-bg text-lg font-bold text-error">
          !
        </div>
        <div className="flex-1 space-y-2">
          <h3 className="font-serif text-xl text-text-primary">{error.title}</h3>
          <p className="text-sm leading-relaxed text-text-muted">{error.message}</p>
        </div>
      </div>
    </section>
  );
}
