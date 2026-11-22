"use client";

import { useEffect, useMemo, useState } from "react";
import { AppHeader } from "@/components/AppHeader";
import { MetricStrip } from "@/components/MetricStrip";
import {
  PreferenceForm,
  type PreferenceFormValues,
} from "@/components/PreferenceForm";
import { RecommendationCard } from "@/components/RecommendationCard";
import { RequestDetails } from "@/components/RequestDetails";
import { StatusLine } from "@/components/StatusLine";
import {
  EmptyCard,
  ErrorCard,
  LoadingCard,
} from "@/components/StateCards";
import { SummaryBanner } from "@/components/SummaryBanner";
import { fetchMeta, postRecommend } from "@/lib/api";
import type {
  MetaResponse,
  PreferenceInput,
  RecommendationResponse,
  UiError,
} from "@/lib/types";

const DEFAULT_CUISINES = [
  "North Indian",
  "Chinese",
  "South Indian",
  "Fast Food",
  "Biryani",
  "Cafe",
  "Italian",
  "Continental",
  "Desserts",
  "Street Food",
];

export default function HomePage() {
  const [meta, setMeta] = useState<MetaResponse | null>(null);
  const [bootError, setBootError] = useState<UiError | null>(null);
  const [form, setForm] = useState<PreferenceFormValues>({
    location: "",
    budget: "medium",
    cuisine: "Italian",
    cuisineCustom: "",
    minRating: 4.0,
    topK: 5,
    additionalPreferences: "",
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RecommendationResponse | null>(null);
  const [error, setError] = useState<UiError | null>(null);
  const [lastPrefs, setLastPrefs] = useState<PreferenceInput | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await fetchMeta();
        if (cancelled) return;
        setMeta(data);
        const defaultLocation = data.locations.includes("Indiranagar")
          ? "Indiranagar"
          : data.locations[0] || "";
        const defaultCuisine = data.popular_cuisines.includes("Italian")
          ? "Italian"
          : data.popular_cuisines[0] || "Italian";
        setForm((prev) => ({
          ...prev,
          location: defaultLocation,
          cuisine: defaultCuisine,
        }));
      } catch (err) {
        if (cancelled) return;
        setBootError(err as UiError);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const cuisines = useMemo(
    () => meta?.popular_cuisines?.length ? meta.popular_cuisines : DEFAULT_CUISINES,
    [meta],
  );

  async function handleSubmit(prefs: PreferenceInput) {
    setLoading(true);
    setError(null);
    setResult(null);
    setLastPrefs(prefs);
    try {
      const response = await postRecommend(prefs);
      setResult(response);
    } catch (err) {
      setError(err as UiError);
    } finally {
      setLoading(false);
    }
  }

  const empty =
    result &&
    result.recommendations.length === 0 &&
    Boolean(result.meta.message);

  const summaryTitle = useMemo(() => {
    if (!result || !lastPrefs) return "";
    if (result.summary?.trim()) return result.summary.trim();
    const count = result.recommendations.length;
    const noun = count === 1 ? "spot" : "spots";
    return `${count} ${lastPrefs.cuisine} ${noun} in ${lastPrefs.location} match a ${lastPrefs.budget} budget and a ${lastPrefs.min_rating.toFixed(1)}+ rating.`;
  }, [result, lastPrefs]);

  return (
    <main className="mx-auto min-h-screen max-w-feed space-y-7 px-4 py-10 sm:px-6 lg:px-8">
      <AppHeader
        mode={meta?.mode || "…"}
        model={meta?.model || "loading"}
      />

      {bootError ? <ErrorCard error={bootError} /> : null}

      {!bootError ? (
        <>
          <PreferenceForm
            values={form}
            locations={meta?.locations?.length ? meta.locations : [form.location || "…"]}
            cuisines={cuisines}
            restaurantCount={meta?.restaurant_count ?? 0}
            disabled={!meta || loading}
            submitting={loading}
            onChange={setForm}
            onSubmit={handleSubmit}
          />

          <StatusLine restaurantCount={meta?.restaurant_count ?? 0} />

          {loading ? (
            <LoadingCard restaurantCount={meta?.restaurant_count ?? 0} />
          ) : null}

          {error ? <ErrorCard error={error} /> : null}

          {empty ? <EmptyCard message={result?.meta.message} /> : null}

          {result && !empty && !loading ? (
            <div className="stagger space-y-6">
              <MetricStrip
                candidateCount={result.meta.candidate_count}
                hardMatchCount={result.meta.hard_match_count}
                results={result.recommendations.length}
              />
              <SummaryBanner
                title={summaryTitle}
                detail={
                  result.meta.used_fallback
                    ? result.meta.message ||
                      "Showing rating-based matches because AI ranking was unavailable."
                    : "Filtered from the Zomato dataset, then ranked with an explanation for each fit."
                }
                warn={result.meta.used_fallback}
              />
              <section className="space-y-3.5" aria-label="Recommendations">
                {result.recommendations.map((item) => (
                  <RecommendationCard key={`${item.restaurant_id}-${item.rank}`} item={item} />
                ))}
              </section>
              <RequestDetails
                meta={result.meta}
                results={result.recommendations.length}
              />
            </div>
          ) : null}
        </>
      ) : null}
    </main>
  );
}
