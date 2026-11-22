"use client";

import type { FormEvent } from "react";
import type { BudgetBand, PreferenceInput } from "@/lib/types";

export type PreferenceFormValues = {
  location: string;
  budget: BudgetBand;
  cuisine: string;
  cuisineCustom: string;
  minRating: number;
  topK: number;
  additionalPreferences: string;
};

type PreferenceFormProps = {
  values: PreferenceFormValues;
  locations: string[];
  cuisines: string[];
  restaurantCount: number;
  disabled?: boolean;
  submitting?: boolean;
  onChange: (next: PreferenceFormValues) => void;
  onSubmit: (prefs: PreferenceInput) => void;
};

const BUDGETS: BudgetBand[] = ["low", "medium", "high"];

export function PreferenceForm({
  values,
  locations,
  cuisines,
  restaurantCount,
  disabled = false,
  submitting = false,
  onChange,
  onSubmit,
}: PreferenceFormProps) {
  function update<K extends keyof PreferenceFormValues>(
    key: K,
    value: PreferenceFormValues[K],
  ) {
    onChange({ ...values, [key]: value });
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const cuisine = values.cuisineCustom.trim() || values.cuisine;
    onSubmit({
      location: values.location,
      budget: values.budget,
      cuisine,
      min_rating: values.minRating,
      additional_preferences: values.additionalPreferences.trim(),
      top_k: values.topK,
    });
  }

  return (
    <section className="animate-fadeUp relative rounded-custom border border-border bg-card p-6 shadow-2xl sm:p-8">
      <div className="mb-6 flex items-center justify-between border-b border-border/60 pb-5">
        <div>
          <h2 className="font-serif text-xl tracking-tight text-text-primary sm:text-2xl">
            Your preferences
          </h2>
          <p className="mt-0.5 text-xs text-text-muted sm:text-sm">
            Define your dining filters to query {restaurantCount.toLocaleString()}{" "}
            curated entries.
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 gap-5 md:grid-cols-12">
          <div className="space-y-2 md:col-span-6">
            <label
              htmlFor="location"
              className="block text-xs font-semibold uppercase tracking-wide text-text-muted"
            >
              Location
            </label>
            <select
              id="location"
              disabled={disabled}
              value={values.location}
              onChange={(e) => update("location", e.target.value)}
              className="h-11 w-full cursor-pointer appearance-none rounded-custom border border-border bg-card-alt px-3.5 text-sm text-text-primary outline-none transition focus:border-accent focus:ring-1 focus:ring-accent disabled:opacity-60"
            >
              {locations.map((loc) => (
                <option key={loc} value={loc}>
                  {loc}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-2 md:col-span-6">
            <span className="block text-xs font-semibold uppercase tracking-wide text-text-muted">
              Budget
            </span>
            <div
              className="grid h-11 grid-cols-3 items-center gap-1 rounded-custom border border-border bg-card-alt p-1"
              role="radiogroup"
              aria-label="Budget"
            >
              {BUDGETS.map((band) => {
                const selected = values.budget === band;
                return (
                  <button
                    key={band}
                    type="button"
                    disabled={disabled}
                    onClick={() => update("budget", band)}
                    className={
                      selected
                        ? "h-9 rounded-[10px] border border-border/80 bg-[#242424] text-xs font-semibold text-text-primary shadow-sm"
                        : "h-9 rounded-[10px] text-xs font-medium text-text-muted transition hover:text-text-primary"
                    }
                  >
                    {band.charAt(0).toUpperCase() + band.slice(1)}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-5 md:grid-cols-12">
          <div className="space-y-2 md:col-span-6">
            <label
              htmlFor="cuisine"
              className="block text-xs font-semibold uppercase tracking-wide text-text-muted"
            >
              Cuisine
            </label>
            <select
              id="cuisine"
              disabled={disabled}
              value={values.cuisine}
              onChange={(e) => update("cuisine", e.target.value)}
              className="h-11 w-full cursor-pointer appearance-none rounded-custom border border-border bg-card-alt px-3.5 text-sm text-text-primary outline-none transition focus:border-accent focus:ring-1 focus:ring-accent disabled:opacity-60"
            >
              {cuisines.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-2 md:col-span-6">
            <div className="flex items-center justify-between">
              <label
                htmlFor="cuisine-custom"
                className="block text-xs font-semibold uppercase tracking-wide text-text-muted"
              >
                Or type a cuisine
              </label>
              <span className="text-[11px] text-text-muted/60">Optional</span>
            </div>
            <input
              id="cuisine-custom"
              type="text"
              disabled={disabled}
              placeholder="e.g. Thai"
              value={values.cuisineCustom}
              onChange={(e) => update("cuisineCustom", e.target.value)}
              className="h-11 w-full rounded-custom border border-border bg-card-alt px-3.5 text-sm text-text-primary outline-none transition placeholder:text-text-muted/40 focus:border-accent focus:ring-1 focus:ring-accent disabled:opacity-60"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 gap-5 pt-1 md:grid-cols-12">
          <div className="space-y-2.5 rounded-custom border border-border/60 bg-inset p-4 md:col-span-6">
            <div className="flex items-center justify-between">
              <label
                htmlFor="min-rating"
                className="text-xs font-semibold uppercase tracking-wide text-text-muted"
              >
                Minimum rating
              </label>
              <span className="rounded border border-accent/20 bg-accent/10 px-2 py-0.5 font-mono text-sm font-semibold text-accent">
                {values.minRating.toFixed(1)}
              </span>
            </div>
            <input
              id="min-rating"
              type="range"
              min={0}
              max={5}
              step={0.1}
              disabled={disabled}
              value={values.minRating}
              onChange={(e) => update("minRating", Number(e.target.value))}
            />
            <div className="flex justify-between px-0.5 font-mono text-[10px] text-text-muted/50">
              <span>0.0</span>
              <span>2.5</span>
              <span>5.0</span>
            </div>
          </div>

          <div className="space-y-2.5 rounded-custom border border-border/60 bg-inset p-4 md:col-span-6">
            <div className="flex items-center justify-between">
              <label
                htmlFor="top-k"
                className="text-xs font-semibold uppercase tracking-wide text-text-muted"
              >
                How many recommendations?
              </label>
              <span className="rounded border border-accent/20 bg-accent/10 px-2.5 py-0.5 font-mono text-sm font-semibold text-accent">
                {values.topK} places
              </span>
            </div>
            <input
              id="top-k"
              type="range"
              min={1}
              max={10}
              step={1}
              disabled={disabled}
              value={values.topK}
              onChange={(e) => update("topK", Number(e.target.value))}
            />
            <div className="flex justify-between px-0.5 font-mono text-[10px] text-text-muted/50">
              <span>1</span>
              <span>5</span>
              <span>10</span>
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <label
            htmlFor="additional"
            className="block text-xs font-semibold uppercase tracking-wide text-text-muted"
          >
            Additional preferences
          </label>
          <input
            id="additional"
            type="text"
            disabled={disabled}
            placeholder="e.g. family-friendly, cafe, outdoor seating"
            value={values.additionalPreferences}
            onChange={(e) => update("additionalPreferences", e.target.value)}
            className="h-11 w-full rounded-custom border border-border bg-card-alt px-3.5 text-sm text-text-primary outline-none transition placeholder:text-text-muted/40 focus:border-accent focus:ring-1 focus:ring-accent disabled:opacity-60"
          />
        </div>

        <div className="pt-2">
          <button
            type="submit"
            disabled={disabled || submitting}
            className="flex h-12 w-full items-center justify-center gap-2 rounded-custom bg-accent text-sm font-semibold tracking-wide text-canvas shadow-lg shadow-accent/10 transition hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-70"
          >
            {submitting ? (
              <span className="animate-pulseSoft">Finding matches…</span>
            ) : (
              <>
                <span>Get recommendations</span>
                <span aria-hidden>→</span>
              </>
            )}
          </button>
        </div>
      </form>
    </section>
  );
}
