export type UserCoords = {
  lat: number;
  lon: number;
};

export type GeoErrorKind = "unsupported" | "denied" | "unavailable" | "timeout";

export class GeoError extends Error {
  kind: GeoErrorKind;

  constructor(kind: GeoErrorKind, message: string) {
    super(message);
    this.kind = kind;
    this.name = "GeoError";
  }
}

let cachedCoords: UserCoords | null = null;
let cachedAt = 0;
const CACHE_MS = 5 * 60_000;

export function destinationQuery(input: {
  name: string;
  address?: string;
  location?: string;
}): string {
  const parts = [
    input.name?.trim(),
    input.address?.trim() || input.location?.trim(),
    "Bangalore",
  ].filter(Boolean);
  return parts.join(", ");
}

export function haversineKm(
  a: UserCoords,
  b: { lat: number; lon: number },
): number {
  const toRad = (deg: number) => (deg * Math.PI) / 180;
  const earthKm = 6371;
  const dLat = toRad(b.lat - a.lat);
  const dLon = toRad(b.lon - a.lon);
  const lat1 = toRad(a.lat);
  const lat2 = toRad(b.lat);
  const h =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) ** 2;
  return earthKm * 2 * Math.atan2(Math.sqrt(h), Math.sqrt(1 - h));
}

export function formatDistanceKm(km: number): string {
  if (!Number.isFinite(km)) return "Distance unavailable";
  if (km < 1) return `~${Math.round(km * 1000)} m away`;
  return `~${km.toFixed(1)} km away`;
}

export function googleMapsDirectionsUrl(options: {
  destination: string;
  origin?: UserCoords | null;
}): string {
  const params = new URLSearchParams({
    api: "1",
    destination: options.destination,
    travelmode: "driving",
  });
  if (options.origin) {
    params.set("origin", `${options.origin.lat},${options.origin.lon}`);
  }
  return `https://www.google.com/maps/dir/?${params.toString()}`;
}

export function getCachedPosition(): UserCoords | null {
  if (!cachedCoords) return null;
  if (Date.now() - cachedAt > CACHE_MS) return null;
  return cachedCoords;
}

export function getCurrentPosition(): Promise<UserCoords> {
  const fresh = getCachedPosition();
  if (fresh) return Promise.resolve(fresh);

  return new Promise((resolve, reject) => {
    if (typeof navigator === "undefined" || !navigator.geolocation) {
      reject(
        new GeoError(
          "unsupported",
          "This browser does not support location access.",
        ),
      );
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        cachedCoords = {
          lat: pos.coords.latitude,
          lon: pos.coords.longitude,
        };
        cachedAt = Date.now();
        resolve(cachedCoords);
      },
      (err) => {
        if (err.code === err.PERMISSION_DENIED) {
          reject(
            new GeoError(
              "denied",
              "Location permission was denied. You can still open Google Maps for directions.",
            ),
          );
          return;
        }
        if (err.code === err.TIMEOUT) {
          reject(
            new GeoError(
              "timeout",
              "Timed out while reading your location. Try again.",
            ),
          );
          return;
        }
        reject(
          new GeoError(
            "unavailable",
            "Could not read your current location.",
          ),
        );
      },
      {
        enableHighAccuracy: false,
        timeout: 4000,
        maximumAge: CACHE_MS,
      },
    );
  });
}
