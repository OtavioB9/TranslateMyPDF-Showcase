import axios from 'axios';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

let api = axios;

if (USE_MOCK) {
  // Em desenvolvimento com Mock ativado, usamos a lógica de simulação
  // Usamos require/import dinâmico ou importação direta se preferir simplicidade
  // Para garantir o melhor tree-shaking em produção, o bloco abaixo
  // só deve ser ativado se USE_MOCK for explicitamente true.
  const mockApi = await import('./api.mock').then(m => m.default);
  api = mockApi;
}

export default api;
