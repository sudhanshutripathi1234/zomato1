type SummaryBannerProps = {
  title: string;
  detail: string;
  warn?: boolean;
};

export function SummaryBanner({ title, detail, warn = false }: SummaryBannerProps) {
  return (
    <section
      className={
        warn
          ? "flex items-start gap-3 rounded-custom border border-warning-border bg-warning-bg p-4 shadow-sm"
          : "flex items-start gap-3 rounded-custom border border-border bg-card-alt p-4 shadow-sm"
      }
    >
      <div
        className={
          warn
            ? "mt-0.5 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-lg border border-warning-border text-sm font-bold text-warning"
            : "mt-0.5 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-lg border border-accent/20 bg-accent/10 text-sm font-bold text-accent"
        }
      >
        i
      </div>
      <div className="flex-1">
        <p className="text-sm font-medium text-text-primary">{title}</p>
        <p className="mt-0.5 text-xs text-text-muted">{detail}</p>
      </div>
    </section>
  );
}
