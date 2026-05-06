import axios from 'axios';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

let api = axios;

if (USE_MOCK) {
  const mockApi = await import('./api.mock').then(m => m.default);
  api = mockApi;
}

export default api;
