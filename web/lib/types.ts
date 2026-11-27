export type BudgetBand = "low" | "medium" | "high";

export type PreferenceInput = {
  location: string;
  budget: BudgetBand;
  cuisine: string;
  min_rating: number;
  additional_preferences: string;
  top_k: number;
};

export type FilterMeta = {
  filters_applied: string[];
  candidate_count: number;
  hard_match_count: number;
  message?: string | null;
  used_llm: boolean;
  used_fallback: boolean;
  llm_provider?: string | null;
};

export type RecommendationItem = {
  rank: number;
  restaurant_id: string;
  name: string;
  cuisine: string;
  rating: number | null;
  estimated_cost: number | null;
  location: string;
  address?: string;
  url?: string;
  explanation: string;
};

export type GeocodeResponse = {
  lat: number;
  lon: number;
  display_name?: string;
};

export type RecommendationResponse = {
  summary: string;
  recommendations: RecommendationItem[];
  meta: FilterMeta;
};

export type MetaResponse = {
  locations: string[];
  restaurant_count: number;
  mode: string;
  model: string;
  use_mock_llm: boolean;
  popular_cuisines: string[];
};

export type UiErrorKind = "api_key" | "dataset" | "generic";

export type UiError = {
  kind: UiErrorKind;
  title: string;
  message: string;
};
