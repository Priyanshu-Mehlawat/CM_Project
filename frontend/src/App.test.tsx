import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, expect, test, vi } from 'vitest';
import App from './App';
import { loadDemo } from './api';
const health = { schema_version: 'v1', service_alive: true, model_available: false, mode: 'synthetic_demo' };
const info = { ...health, name: 'RENAL-GUARD', version: '0.1.0', research_mode_enabled: false, model_version: null, evaluation_state: 'not_yet_evaluated', protocol_state: 'pending_G1' };
const cases = { schema_version: 'v1', cases: [{ schema_version: 'v1', id: 'synthetic-a', name: 'Example A', description: 'Invented fixture', source: 'independently_authored_synthetic', model_state: 'unavailable', probability: null, clinical_stage: null }] };
function mockApi(payload = cases) {
  vi.stubGlobal('fetch', vi.fn(async (url: string) => ({ ok: true, json: async () => url.endsWith('/health') ? health : url.endsWith('/system/info') ? info : payload })));
}
afterEach(() => vi.unstubAllGlobals());
test('demo connects, opens synthetic case, and navigates to honest research empty state', async () => {
  mockApi();
  render(<MemoryRouter><App /></MemoryRouter>);
  expect(screen.getByText('SYNTHETIC DEMO')).toBeVisible();
  fireEvent.click(await screen.findByRole('button', { name: /Example A/ }));
  expect(screen.getByText('Invented fixture')).toBeVisible();
  expect(screen.getByText('Unavailable · clinical engine pending')).toBeVisible();
  expect(screen.getAllByText('Model unavailable').length).toBeGreaterThan(0);
  fireEvent.click(screen.getByRole('link', { name: /Research Console/ }));
  expect(screen.getByRole('heading', { name: 'Research Console' })).toBeVisible();
  expect(screen.getByRole('heading', { name: 'Not yet evaluated' })).toBeVisible();
});
test('failed backend shows no example data and supports retry', async () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));
  render(<MemoryRouter><App /></MemoryRouter>);
  expect(await screen.findByRole('alert')).toHaveTextContent('Backend unavailable');
  expect(screen.queryByText('Example A')).not.toBeInTheDocument();
  mockApi();
  fireEvent.click(screen.getByRole('button', { name: 'Retry connection' }));
  expect(await screen.findByRole('button', { name: /Example A/ })).toBeVisible();
});
test('empty case list remains useful', async () => {
  mockApi({ schema_version: 'v1', cases: [] });
  render(<MemoryRouter><App /></MemoryRouter>);
  expect(await screen.findByText('No synthetic examples are available.')).toBeVisible();
});
test('incompatible scores fail closed rather than appearing as real inference', async () => {
  vi.stubGlobal('fetch', vi.fn(async (url: string) => ({ ok: true, json: async () => url.endsWith('/health') ? health : url.endsWith('/system/info') ? info : { ...cases, cases: [{ ...cases.cases[0], probability: 0.75 }] } })));
  await expect(loadDemo(new AbortController().signal)).rejects.toThrow('Incompatible API contract');
});
