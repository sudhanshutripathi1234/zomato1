type StatusLineProps = {
  restaurantCount: number;
};

export function StatusLine({ restaurantCount }: StatusLineProps) {
  return (
    <div className="flex items-center justify-center gap-2 py-0.5 text-xs tracking-wide text-text-muted">
      <span className="h-1.5 w-1.5 rounded-full bg-accent/70" />
      <span>
        Dataset ready · {restaurantCount.toLocaleString()} restaurants cached.
      </span>
    </div>
  );
}
