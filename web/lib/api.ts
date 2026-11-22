import type {
  MetaResponse,
  PreferenceInput,
  RecommendationResponse,
  UiError,
} from "./types";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

async function readError(res: Response): Promise<UiError> {
  let detail = "";
  try {
    const data = await res.json();
    detail = typeof data?.detail === "string" ? data.detail : JSON.stringify(data?.detail ?? data);
  } catch {
    detail = await res.text();
  }

  if (res.status === 401 || /api key|groq/i.test(detail)) {
    return {
      kind: "api_key",
      title: "Groq API key is missing or invalid.",
      message:
        detail ||
        "Set GROQ_API_KEY in .env, or set USE_MOCK_LLM=true for offline demo mode.",
    };
  }
  if (res.status === 503 || /dataset|parquet|huggingface/i.test(detail)) {
    return {
      kind: "dataset",
      title: "Could not load the restaurant dataset.",
      message:
        detail ||
        "Check your network, DATA_CACHE_PATH, or regenerate the local parquet cache.",
    };
  }
  return {
    kind: "generic",
    title: "Something went wrong.",
    message: detail || `Request failed with status ${res.status}`,
  };
}

export async function fetchMeta(): Promise<MetaResponse> {
  const res = await fetch(`${API_URL}/meta`, { cache: "no-store" });
  if (!res.ok) {
    throw await readError(res);
  }
  return res.json();
}

export async function postRecommend(
  prefs: PreferenceInput,
): Promise<RecommendationResponse> {
  const res = await fetch(`${API_URL}/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(prefs),
  });
  if (!res.ok) {
    throw await readError(res);
  }
  return res.json();
}

export { API_URL };
