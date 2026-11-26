"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import gsap from "gsap";
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
import { RevealList } from "@/components/RevealList";
import { RiseIn } from "@/components/RiseIn";
import { SummaryBanner } from "@/components/SummaryBanner";
import { fetchMeta, postRecommend } from "@/lib/api";
import { prefersReducedMotion, registerMotion } from "@/lib/motion";
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
  const stageRef = useRef<HTMLDivElement>(null);

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

  useEffect(() => {
    if (!loading && !result && !error) return;
    const el = stageRef.current;
    if (!el) return;
    const top = el.getBoundingClientRect().top;
    if (top >= 12 && top < window.innerHeight * 0.55) return;

    if (prefersReducedMotion()) {
      el.scrollIntoView({ block: "start" });
      return;
    }

    registerMotion();
    gsap.to(window, {
      duration: 0.65,
      ease: "power2.inOut",
      scrollTo: { y: el, offsetY: 20 },
      overwrite: "auto",
    });
  }, [loading, result, error]);

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

      {bootError ? (
        <RiseIn>
          <ErrorCard error={bootError} />
        </RiseIn>
      ) : null}

      {!bootError ? (
        <>
          <RiseIn delay={0.18} className="space-y-7">
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
          </RiseIn>

          <div ref={stageRef} className="scroll-mt-4 space-y-6">
          {loading ? (
            <LoadingCard restaurantCount={meta?.restaurant_count ?? 0} />
          ) : null}

          {error ? (
            <RiseIn>
              <ErrorCard error={error} />
            </RiseIn>
          ) : null}

          {empty ? (
            <RiseIn>
              <EmptyCard message={result?.meta.message} />
            </RiseIn>
          ) : null}

          {result && !empty && !loading ? (
            <RevealList
              className="space-y-6"
              watch={result.recommendations
                .map((item) => `${item.restaurant_id}-${item.rank}`)
                .join("|")}
            >
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
            </RevealList>
          ) : null}
          </div>
        </>
      ) : null}
    </main>
  );
}
