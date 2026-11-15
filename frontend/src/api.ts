import { contractSchemas } from "./generated/contracts";
import type {
  EpisodeList,
  EpisodeView,
  Health,
  ResearchStatus,
  SystemInfo,
} from "./generated/contracts";
export type { EpisodeView };
export interface DemoState {
  health: Health;
  info: SystemInfo;
  cases: EpisodeList["episodes"];
  research: ResearchStatus;
}
type Schema = {
  type?: string;
  const?: unknown;
  enum?: readonly unknown[];
  anyOf?: readonly Schema[];
  $ref?: string;
  $defs?: Record<string, Schema>;
  required?: readonly string[];
  properties?: Record<string, Schema>;
  items?: Schema;
  additionalProperties?: boolean;
};
function matches(
  value: unknown,
  schema: Schema,
  defs: Record<string, Schema>,
): boolean {
  if (schema.$ref)
    return matches(value, defs[schema.$ref.split("/").at(-1)!], defs);
  if ("const" in schema && value !== schema.const) return false;
  if (schema.enum && !schema.enum.includes(value)) return false;
  if (schema.anyOf) return schema.anyOf.some((s) => matches(value, s, defs));
  switch (schema.type) {
    case "null":
      return value === null;
    case "string":
      return typeof value === "string";
    case "boolean":
      return typeof value === "boolean";
    case "number":
      return typeof value === "number" && Number.isFinite(value);
    case "integer":
      return typeof value === "number" && Number.isInteger(value);
    case "array":
      return (
        Array.isArray(value) &&
        value.every((v) => matches(v, schema.items!, defs))
      );
    case "object": {
      if (!value || typeof value !== "object" || Array.isArray(value))
        return false;
      const obj = value as Record<string, unknown>;
      return (
        (schema.required ?? []).every((k) => k in obj) &&
        Object.entries(obj).every(([k, v]) =>
          schema.properties?.[k]
            ? matches(v, schema.properties[k], defs)
            : schema.additionalProperties !== false,
        )
      );
    }
    default:
      return true;
  }
}
export async function getContract<T>(
  path: string,
  name: keyof typeof contractSchemas,
  signal: AbortSignal,
): Promise<T> {
  const response = await fetch(`/api/v1/${path}`, { signal });
  if (!response.ok) throw new Error(`API request failed (${response.status})`);
  const data: unknown = await response.json();
  const schema: Schema = contractSchemas[name];
  if (!matches(data, schema, schema.$defs ?? {}))
    throw new Error("Incompatible API contract");
  return data as T;
}
export async function loadDemo(signal: AbortSignal): Promise<DemoState> {
  const [health, info, payload, research] = await Promise.all([
    getContract<Health>("health", "Health", signal),
    getContract<SystemInfo>("system/info", "SystemInfo", signal),
    getContract<EpisodeList>("episodes", "EpisodeList", signal),
    getContract<ResearchStatus>("research/status", "ResearchStatus", signal),
  ]);
  return { health, info, cases: payload.episodes, research };
}
export function loadEpisode(id: string, hour: number, signal: AbortSignal) {
  return getContract<EpisodeView>(
    `episodes/${encodeURIComponent(id)}?cutoff_hour=${hour}`,
    "EpisodeView",
    signal,
  );
}
