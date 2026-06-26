import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * A general purpose React hook for executing API requests.
 * 
 * @param {string|Function} urlOrFn The URL to fetch or a function returning the URL
 * @param {object} fetchOptions Options to pass to the fetch call
 * @param {boolean} lazy If true, does not fetch automatically on mount
 */
export function useApi(urlOrFn, fetchOptions = {}, lazy = false) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(!lazy);
  const [error, setError] = useState(null);

  const urlOrFnRef = useRef(urlOrFn);
  const optionsRef = useRef(fetchOptions);

  // Keep refs up to date
  useEffect(() => {
    urlOrFnRef.current = urlOrFn;
    optionsRef.current = fetchOptions;
  }, [urlOrFn, fetchOptions]);

  const execute = useCallback(async (optionsOverride = {}) => {
    setLoading(true);
    setError(null);
    try {
      const url = typeof urlOrFnRef.current === 'function' ? urlOrFnRef.current() : urlOrFnRef.current;
      if (!url) return;

      const mergedOptions = {
        ...optionsRef.current,
        ...optionsOverride,
        headers: {
          ...(optionsRef.current ? optionsRef.current.headers : {}),
          ...optionsOverride.headers,
        }
      };

      const response = await fetch(url, mergedOptions);
      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
      }
      const json = await response.json();
      setData(json);
      return json;
    } catch (err) {
      console.error("API Call failed:", err);
      setError(err.message || 'Something went wrong');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!lazy) {
      execute().catch(() => {});
    }
  }, [lazy, execute]);

  return { data, loading, error, execute, setData };
}
