export interface Health {
  schema_version: 'v1'; service_alive: boolean; model_available: false; mode: 'synthetic_demo';
}
export interface DemoCase {
  schema_version: 'v1'; id: string; name: string; description: string;
  source: 'independently_authored_synthetic'; model_state: 'unavailable';
  probability: null; clinical_stage: null;
}
export interface SystemInfo {
  schema_version: 'v1'; name: string; version: string; mode: 'synthetic_demo';
  research_mode_enabled: false; model_available: false; model_version: null;
  evaluation_state: 'not_yet_evaluated'; protocol_state: 'pending_G1';
}
export interface DemoState { health: Health; info: SystemInfo; cases: DemoCase[] }
async function get(path: string, signal: AbortSignal): Promise<unknown> {
  const response = await fetch(`/api/v1/${path}`, { signal });
  if (!response.ok) throw new Error('API unavailable');
  return response.json();
}
function object(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}
export async function loadDemo(signal: AbortSignal): Promise<DemoState> {
  const [health, info, payload] = await Promise.all([
    get('health', signal), get('system/info', signal), get('demo/cases', signal),
  ]);
  // Fail closed if the server is incompatible with this synthetic-only shell.
  if (!object(health) || health.schema_version !== 'v1' || health.service_alive !== true ||
      health.mode !== 'synthetic_demo' || health.model_available !== false ||
      !object(info) || info.schema_version !== 'v1' || info.mode !== 'synthetic_demo' ||
      info.model_available !== false || info.research_mode_enabled !== false ||
      info.model_version !== null || info.evaluation_state !== 'not_yet_evaluated' ||
      info.protocol_state !== 'pending_G1' || typeof info.name !== 'string' ||
      typeof info.version !== 'string' || !object(payload) || payload.schema_version !== 'v1' ||
      !Array.isArray(payload.cases) || !payload.cases.every((item: unknown) =>
        object(item) && item.schema_version === 'v1' && typeof item.id === 'string' &&
        typeof item.name === 'string' && typeof item.description === 'string' &&
        item.source === 'independently_authored_synthetic' && item.model_state === 'unavailable' &&
        item.probability === null && item.clinical_stage === null)) {
    throw new Error('Incompatible API contract');
  }
  return { health: health as unknown as Health, info: info as unknown as SystemInfo,
    cases: payload.cases as DemoCase[] };
}
