type MetricStripProps = {
  candidateCount: number;
  hardMatchCount: number;
  results: number;
};

export function MetricStrip({
  candidateCount,
  hardMatchCount,
  results,
}: MetricStripProps) {
  return (
    <section className="grid grid-cols-1 gap-3 sm:grid-cols-3">
      <div className="flex items-center justify-between rounded-custom border border-border bg-card px-4 py-3.5">
        <span className="text-xs font-medium text-text-muted">
          Candidates sent to AI
        </span>
        <span className="rounded border border-border/80 bg-[#1A1A1A] px-2 py-0.5 font-mono text-base font-bold text-text-primary">
          {candidateCount}
        </span>
      </div>
      <div className="flex items-center justify-between rounded-custom border border-border bg-card px-4 py-3.5">
        <span className="text-xs font-medium text-text-muted">
          Hard filter matches
        </span>
        <span className="rounded border border-border/80 bg-[#1A1A1A] px-2 py-0.5 font-mono text-base font-bold text-text-primary">
          {hardMatchCount}
        </span>
      </div>
      <div className="flex items-center justify-between rounded-custom border border-border bg-card px-4 py-3.5">
        <span className="text-xs font-medium text-text-muted">Results</span>
        <span className="rounded border border-accent/30 bg-accent/10 px-2.5 py-0.5 font-mono text-base font-bold text-accent">
          {results}
        </span>
      </div>
    </section>
  );
}
