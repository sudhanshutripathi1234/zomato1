type AppHeaderProps = {
  mode: string;
  model: string;
};

export function AppHeader({ mode, model }: AppHeaderProps) {
  const chip =
    mode.toLowerCase().includes("mock") || model === "mock"
      ? "Mode: Mock LLM · offline"
      : `Mode: ${mode} · ${model}`;

  return (
    <header className="space-y-3 pt-2">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="font-serif text-3xl tracking-tight text-text-primary sm:text-4xl lg:text-[42px] lg:leading-[1.15]">
          Restaurant Recommender
        </h1>
        <div className="inline-flex items-center gap-2 rounded-full border border-border bg-card-alt px-3 py-1.5 text-[11px] tracking-wide text-text-muted">
          <span className="h-1.5 w-1.5 rounded-full bg-accent" />
          <span>{chip}</span>
        </div>
      </div>
      <p className="max-w-2xl text-base font-normal leading-relaxed text-text-muted sm:text-lg">
        Filter real Zomato listings, then let AI rank and explain the best fits.
      </p>
    </header>
  );
}
