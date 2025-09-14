// Centralized environment access
export const API_BASE = (() => {
  const val = import.meta.env.VITE_API_BASE;
  if (!val) {
    // Non-fatal: fetch helper will still throw on use.
    console.warn('[config] VITE_API_BASE not set. API calls will fail.');
  }
  return val || '';
})();